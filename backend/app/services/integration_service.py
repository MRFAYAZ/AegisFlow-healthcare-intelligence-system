"""Authenticated, facility-scoped inventory snapshot ingestion."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import secrets
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import SeverityEnum, TransferStatusEnum
from app.engines.inventory.medicine_safety import safe_transferable_quantity
from app.models.facility import Facility
from app.models.integration_event import IntegrationEvent
from app.models.integration_medicine_mapping import IntegrationMedicineMapping
from app.models.integration_source import IntegrationSource
from app.models.inventory import InventoryBatch, InventoryCurrent
from app.models.medicine import Medicine
from app.models.redistribution import TransferRequest
from app.models.transfer_batch_allocation import TransferBatchAllocation
from app.schemas.integration import (
    IntegrationInventorySnapshotRequest,
    IntegrationMedicineMappingCreate,
    IntegrationSourceCreate,
)
from app.services.inventory.shortage_service import ShortageService


class InvalidIntegrationCredential(PermissionError):
    """Raised when an integration key is absent, unknown or disabled."""


class IntegrationService:
    """Manages partner credentials/mappings and safely applies inventory snapshots."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _credential_hash(credential: str) -> str:
        return sha256(credential.encode("utf-8")).hexdigest()

    @staticmethod
    def _source_response(source: IntegrationSource) -> dict:
        return {
            "source_id": source.source_id,
            "source_name": source.source_name,
            "system_type": source.system_type,
            "facility_id": source.facility_id,
            "is_active": source.is_active,
            "last_snapshot_at": source.last_snapshot_at,
        }

    def create_source(self, payload: IntegrationSourceCreate, actor) -> dict:
        facility = self.db.get(Facility, payload.facility_id)
        if facility is None:
            raise LookupError("Facility not found.")

        existing = self.db.execute(
            select(IntegrationSource.source_id).where(
                IntegrationSource.facility_id == payload.facility_id
            )
        ).scalar_one_or_none()
        if existing is not None:
            raise ValueError(
                "An authoritative integration source already exists for this facility. "
                "Disable or reconfigure it before creating another source."
            )

        credential = secrets.token_urlsafe(36)
        source = IntegrationSource(
            source_name=payload.source_name.strip(),
            system_type=payload.system_type.strip().upper(),
            facility_id=payload.facility_id,
            credential_hash=self._credential_hash(credential),
            is_active=True,
            created_by=actor.user_id,
        )
        try:
            self.db.add(source)
            self.db.commit()
            self.db.refresh(source)
            return {
                **self._source_response(source),
                "integration_key": credential,
                "credential_note": (
                    "Copy this key now. It is returned only at creation; "
                    "AegisFlow stores its SHA-256 hash, not the raw key."
                ),
            }
        except Exception:
            self.db.rollback()
            raise

    def list_sources(self) -> list[dict]:
        sources = self.db.execute(
            select(IntegrationSource).order_by(IntegrationSource.created_at.desc())
        ).scalars().all()
        return [self._source_response(source) for source in sources]

    def deactivate_source(self, source_id: UUID) -> dict:
        source = self.db.execute(
            select(IntegrationSource)
            .where(IntegrationSource.source_id == source_id)
            .with_for_update()
        ).scalar_one_or_none()
        if source is None:
            raise LookupError("Integration source not found.")
        source.is_active = False
        self.db.commit()
        self.db.refresh(source)
        return self._source_response(source)

    def create_or_update_medicine_mapping(
        self,
        source_id: UUID,
        payload: IntegrationMedicineMappingCreate,
    ) -> dict:
        source = self.db.get(IntegrationSource, source_id)
        if source is None:
            raise LookupError("Integration source not found.")
        medicine = self.db.get(Medicine, payload.medicine_id)
        if medicine is None:
            raise LookupError("AegisFlow medicine not found.")

        try:
            mapping = self.db.execute(
                select(IntegrationMedicineMapping)
                .where(
                    IntegrationMedicineMapping.source_id == source_id,
                    IntegrationMedicineMapping.external_medicine_code == payload.external_medicine_code.strip(),
                )
                .with_for_update()
            ).scalar_one_or_none()

            if mapping is None:
                mapping = IntegrationMedicineMapping(
                    source_id=source_id,
                    external_medicine_code=payload.external_medicine_code.strip(),
                    medicine_id=payload.medicine_id,
                    is_active=True,
                )
                self.db.add(mapping)
            else:
                mapping.medicine_id = payload.medicine_id
                mapping.is_active = True

            self.db.commit()
            self.db.refresh(mapping)
            return {
                "mapping_id": mapping.mapping_id,
                "source_id": mapping.source_id,
                "external_medicine_code": mapping.external_medicine_code,
                "medicine_id": mapping.medicine_id,
                "is_active": mapping.is_active,
            }
        except Exception:
            self.db.rollback()
            raise

    def list_medicine_mappings(self, source_id: UUID) -> list[dict]:
        source = self.db.get(IntegrationSource, source_id)
        if source is None:
            raise LookupError("Integration source not found.")
        mappings = self.db.execute(
            select(IntegrationMedicineMapping)
            .where(IntegrationMedicineMapping.source_id == source_id)
            .order_by(IntegrationMedicineMapping.external_medicine_code.asc())
        ).scalars().all()
        return [
            {
                "mapping_id": mapping.mapping_id,
                "source_id": mapping.source_id,
                "external_medicine_code": mapping.external_medicine_code,
                "medicine_id": mapping.medicine_id,
                "is_active": mapping.is_active,
            }
            for mapping in mappings
        ]

    def _authenticate_source(self, credential: str | None) -> IntegrationSource:
        if not credential:
            raise InvalidIntegrationCredential("Missing X-Integration-Key header.")
        source = self.db.execute(
            select(IntegrationSource)
            .where(IntegrationSource.credential_hash == self._credential_hash(credential))
            .with_for_update()
        ).scalar_one_or_none()
        if source is None or not source.is_active:
            raise InvalidIntegrationCredential("Integration key is invalid or disabled.")
        return source

    def _active_batch_reservations(
        self,
        source_facility_id: UUID,
        medicine_id: UUID,
        batch_ids: list[UUID],
    ) -> dict[UUID, int]:
        if not batch_ids:
            return {}
        rows = self.db.execute(
            select(
                TransferBatchAllocation.batch_id,
                func.sum(TransferBatchAllocation.allocated_quantity),
            )
            .join(
                TransferRequest,
                TransferBatchAllocation.transfer_id == TransferRequest.transfer_id,
            )
            .where(
                TransferBatchAllocation.batch_id.in_(batch_ids),
                TransferRequest.from_facility_id == source_facility_id,
                TransferRequest.medicine_id == medicine_id,
                TransferRequest.transfer_status.in_([
                    TransferStatusEnum.APPROVED,
                    TransferStatusEnum.IN_TRANSIT,
                ]),
            )
            .group_by(TransferBatchAllocation.batch_id)
        ).all()
        return {batch_id: int(quantity or 0) for batch_id, quantity in rows}

    def ingest_inventory_snapshot(
        self,
        credential: str | None,
        payload: IntegrationInventorySnapshotRequest,
    ) -> dict:
        try:
            source = self._authenticate_source(credential)
            serialized_payload = payload.model_dump(mode="json")
            canonical_json = json.dumps(
                serialized_payload,
                sort_keys=True,
                separators=(",", ":"),
            )
            payload_hash = sha256(canonical_json.encode("utf-8")).hexdigest()

            prior_event = self.db.execute(
                select(IntegrationEvent)
                .where(
                    IntegrationEvent.source_id == source.source_id,
                    IntegrationEvent.external_event_id == payload.external_event_id,
                )
                .with_for_update()
            ).scalar_one_or_none()
            if prior_event is not None:
                if prior_event.payload_hash != payload_hash:
                    raise ValueError(
                        "external_event_id was already used with a different payload; "
                        "use a new event ID for changed content."
                    )
                self.db.commit()
                response = dict(prior_event.response_payload or {})
                response["idempotent_replay"] = True
                response["message"] = "Identical snapshot replay accepted; no inventory changes were applied."
                return response

            if source.last_snapshot_at is not None and payload.source_timestamp < source.last_snapshot_at:
                raise ValueError(
                    "Snapshot is stale: source_timestamp is older than the last accepted snapshot."
                )
            now = self._now()
            if payload.source_timestamp > now.replace(microsecond=0) + __import__("datetime").timedelta(minutes=5):
                raise ValueError("source_timestamp is more than five minutes in the future.")

            external_codes = {item.external_medicine_code for item in payload.items}
            mappings = self.db.execute(
                select(IntegrationMedicineMapping).where(
                    IntegrationMedicineMapping.source_id == source.source_id,
                    IntegrationMedicineMapping.is_active.is_(True),
                    IntegrationMedicineMapping.external_medicine_code.in_(external_codes),
                )
            ).scalars().all()
            mapping_by_code = {
                mapping.external_medicine_code: mapping for mapping in mappings
            }
            unmapped = sorted(external_codes - set(mapping_by_code))
            if unmapped:
                raise ValueError(
                    "Snapshot contains unmapped external medicine code(s): "
                    + ", ".join(unmapped[:10])
                )

            facility = self.db.get(Facility, source.facility_id)
            if facility is None or not facility.is_active:
                raise ValueError("The integration source facility is missing or inactive.")

            processed = 0
            for item in payload.items:
                mapping = mapping_by_code[item.external_medicine_code]
                medicine = self.db.get(Medicine, mapping.medicine_id)
                if medicine is None:
                    raise ValueError(
                        f"Mapped medicine for {item.external_medicine_code} no longer exists."
                    )

                inventory = self.db.execute(
                    select(InventoryCurrent)
                    .where(
                        InventoryCurrent.facility_id == source.facility_id,
                        InventoryCurrent.medicine_id == medicine.medicine_id,
                    )
                    .with_for_update()
                ).scalar_one_or_none()

                previous_total = int(inventory.total_stock or 0) if inventory else 0
                if inventory is None:
                    inventory = InventoryCurrent(
                        facility_id=source.facility_id,
                        medicine_id=medicine.medicine_id,
                        total_stock=0,
                        available_stock=0,
                        reserved_stock=0,
                        minimum_threshold=item.minimum_threshold,
                        reorder_threshold=item.reorder_threshold,
                        daily_consumption_rate=item.daily_consumption_rate,
                        lead_time_days=item.lead_time_days,
                        shortage_score=0,
                        severity=SeverityEnum.SAFE,
                        last_restocked_at=payload.source_timestamp,
                    )
                    self.db.add(inventory)
                    self.db.flush()

                existing_batches = self.db.execute(
                    select(InventoryBatch)
                    .where(InventoryBatch.inventory_id == inventory.inventory_id)
                    .with_for_update()
                ).scalars().all()
                existing_by_number = {batch.batch_number: batch for batch in existing_batches}
                existing_ids = [batch.batch_id for batch in existing_batches]
                active_reservations = self._active_batch_reservations(
                    source.facility_id,
                    medicine.medicine_id,
                    existing_ids,
                )

                incoming_numbers = {batch.batch_number for batch in item.batches}
                for existing_batch in existing_batches:
                    if existing_batch.batch_number in incoming_numbers:
                        continue
                    active_reserved = active_reservations.get(existing_batch.batch_id, 0)
                    if active_reserved > 0:
                        raise ValueError(
                            f"Snapshot omitted batch {existing_batch.batch_number}, "
                            "which still has an active AegisFlow transfer reservation."
                        )
                    existing_batch.quantity_available = 0
                    existing_batch.quantity_reserved = 0

                local_available = 0
                local_reserved = 0
                for incoming_batch in item.batches:
                    existing_batch = existing_by_number.get(incoming_batch.batch_number)
                    internal_reserved = (
                        active_reservations.get(existing_batch.batch_id, 0)
                        if existing_batch is not None
                        else 0
                    )
                    if incoming_batch.available_stock < internal_reserved:
                        raise ValueError(
                            f"Snapshot availability for batch {incoming_batch.batch_number} "
                            "is lower than the active AegisFlow reservation."
                        )

                    available_after_internal = incoming_batch.available_stock - internal_reserved
                    reserved_after_internal = incoming_batch.reserved_stock + internal_reserved
                    local_available += available_after_internal
                    local_reserved += reserved_after_internal

                    if existing_batch is None:
                        batch_record = InventoryBatch(
                            inventory_id=inventory.inventory_id,
                            batch_number=incoming_batch.batch_number,
                            supplier_name=incoming_batch.supplier_name,
                            manufacturing_date=incoming_batch.manufacturing_date,
                            expiry_date=incoming_batch.expiry_date,
                            quantity_received=incoming_batch.quantity_received,
                            quantity_available=available_after_internal,
                            quantity_reserved=reserved_after_internal,
                            unit_cost=incoming_batch.unit_cost,
                        )
                        self.db.add(batch_record)
                    else:
                        existing_batch.supplier_name = incoming_batch.supplier_name
                        existing_batch.manufacturing_date = incoming_batch.manufacturing_date
                        existing_batch.expiry_date = incoming_batch.expiry_date
                        existing_batch.quantity_received = incoming_batch.quantity_received
                        existing_batch.quantity_available = available_after_internal
                        existing_batch.quantity_reserved = reserved_after_internal
                        existing_batch.unit_cost = incoming_batch.unit_cost

                computed_total = local_available + local_reserved
                if computed_total != item.total_stock:
                    raise ValueError(
                        f"Inventory total mismatch for {item.external_medicine_code}: "
                        f"snapshot={item.total_stock}, reconciled={computed_total}."
                    )

                inventory.total_stock = computed_total
                inventory.available_stock = local_available
                inventory.reserved_stock = local_reserved
                inventory.minimum_threshold = item.minimum_threshold
                inventory.reorder_threshold = item.reorder_threshold
                inventory.daily_consumption_rate = item.daily_consumption_rate
                inventory.lead_time_days = item.lead_time_days

                inventory.shortage_score = ShortageService.calculate_shortage_score(
                    available_stock=local_available,
                    daily_consumption_rate=float(item.daily_consumption_rate),
                    lead_time_days=item.lead_time_days,
                    safety_stock_days=int(medicine.safety_stock_days or 0),
                )
                inventory.severity = ShortageService.determine_severity(
                    float(inventory.shortage_score)
                )
                if computed_total > previous_total:
                    inventory.last_restocked_at = payload.source_timestamp

                processed += 1

            self.db.flush()
            response = {
                "accepted": True,
                "idempotent_replay": False,
                "source_id": source.source_id,
                "external_event_id": payload.external_event_id,
                "source_timestamp": payload.source_timestamp.isoformat(),
                "records_processed": processed,
                "message": (
                    "Inventory snapshot applied. AegisFlow reservations were preserved, "
                    "and unexpired batch records remain required for donor eligibility."
                ),
            }
            self.db.add(
                IntegrationEvent(
                    source_id=source.source_id,
                    external_event_id=payload.external_event_id,
                    payload_hash=payload_hash,
                    source_timestamp=payload.source_timestamp,
                    status="APPLIED",
                    records_processed=processed,
                    response_payload=response,
                    received_at=now,
                    processed_at=now,
                )
            )
            source.last_snapshot_at = payload.source_timestamp
            self.db.commit()
            return response
        except Exception:
            self.db.rollback()
            raise
