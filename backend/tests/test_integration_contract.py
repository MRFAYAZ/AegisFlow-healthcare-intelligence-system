from datetime import date, datetime, timedelta, timezone
import os
from uuid import uuid4

# Importing the ORM/service layer loads application settings; keep this unit
# test isolated from any developer's real database or signing secret.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "aegisflow-test-only-secret")

import pytest
from pydantic import ValidationError

from app.schemas.integration import (
    IntegrationBatchSnapshot,
    IntegrationInventoryItem,
    IntegrationInventorySnapshotRequest,
    IntegrationSourceCreate,
)
from app.services.integration_service import IntegrationService
from app.engines.integration.snapshot_contract import (
    canonical_snapshot_hash,
    validate_replay_payload,
    validate_snapshot_timestamp,
)


def batch(
    batch_number="B-100",
    manufactured=date(2025, 1, 1),
    expires=date(2027, 1, 1),
    received=100,
    available=80,
    reserved=10,
):
    return IntegrationBatchSnapshot(
        batch_number=batch_number,
        manufacturing_date=manufactured,
        expiry_date=expires,
        quantity_received=received,
        available_stock=available,
        reserved_stock=reserved,
    )


def test_source_names_are_trimmed_and_whitespace_only_values_are_rejected():
    source = IntegrationSourceCreate(
        source_name="  Hospital HIS  ",
        system_type="  hl7-fhir ",
        facility_id=uuid4(),
    )
    assert source.source_name == "Hospital HIS"
    assert source.system_type == "hl7-fhir"

    with pytest.raises(ValidationError):
        IntegrationSourceCreate(
            source_name="   ",
            system_type="ERP",
            facility_id=uuid4(),
        )


def test_snapshot_contract_requires_timezone_and_unique_medicine_lines():
    valid = IntegrationInventorySnapshotRequest(
        external_event_id=" EVT-001 ",
        source_timestamp=datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc),
        items=[
            IntegrationInventoryItem(
                external_medicine_code=" MED-01 ",
                total_stock=90,
                minimum_threshold=5,
                reorder_threshold=10,
                daily_consumption_rate=2,
                lead_time_days=3,
                batches=[batch()],
            )
        ],
    )
    assert valid.external_event_id == "EVT-001"
    assert valid.items[0].external_medicine_code == "MED-01"

    with pytest.raises(ValidationError, match="timezone"):
        IntegrationInventorySnapshotRequest(
            external_event_id="EVT-002",
            source_timestamp=datetime(2026, 10, 14, 10, 0),
            items=[
                IntegrationInventoryItem(
                    external_medicine_code="MED-01",
                    total_stock=90,
                    minimum_threshold=5,
                    reorder_threshold=10,
                    daily_consumption_rate=2,
                    lead_time_days=3,
                    batches=[batch()],
                )
            ],
        )


def test_snapshot_rejects_stock_totals_that_do_not_reconcile_to_batches():
    with pytest.raises(ValidationError, match="total_stock must equal"):
        IntegrationInventoryItem(
            external_medicine_code="MED-01",
            total_stock=91,
            minimum_threshold=5,
            reorder_threshold=10,
            daily_consumption_rate=2,
            lead_time_days=3,
            batches=[batch()],
        )


def test_snapshot_rejects_nonzero_stock_without_batch_traceability():
    with pytest.raises(ValidationError, match="batch-level expiry"):
        IntegrationInventoryItem(
            external_medicine_code="MED-01",
            total_stock=10,
            minimum_threshold=1,
            reorder_threshold=2,
            daily_consumption_rate=1,
            lead_time_days=1,
            batches=[],
        )


def test_snapshot_rejects_duplicate_batches_and_duplicate_medicine_lines():
    with pytest.raises(ValidationError, match="unique within"):
        IntegrationInventoryItem(
            external_medicine_code="MED-01",
            total_stock=180,
            minimum_threshold=5,
            reorder_threshold=10,
            daily_consumption_rate=2,
            lead_time_days=3,
            batches=[batch("B-100"), batch("B-100")],
        )

    with pytest.raises(ValidationError, match="appear once"):
        IntegrationInventorySnapshotRequest(
            external_event_id="EVT-003",
            source_timestamp=datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc),
            items=[
                IntegrationInventoryItem(
                    external_medicine_code="MED-01",
                    total_stock=90,
                    minimum_threshold=5,
                    reorder_threshold=10,
                    daily_consumption_rate=2,
                    lead_time_days=3,
                    batches=[batch()],
                ),
                IntegrationInventoryItem(
                    external_medicine_code="MED-01",
                    total_stock=90,
                    minimum_threshold=5,
                    reorder_threshold=10,
                    daily_consumption_rate=2,
                    lead_time_days=3,
                    batches=[batch("B-200")],
                ),
            ],
        )


def test_batch_manufacturing_and_expiry_dates_are_consistent():
    with pytest.raises(ValidationError, match="expiry_date cannot precede"):
        batch(
            manufactured=date(2027, 1, 1),
            expires=date(2026, 1, 1),
        )



def test_integration_key_storage_uses_a_one_way_sha256_digest():
    raw_key = "test-only-high-entropy-token"
    digest = IntegrationService._credential_hash(raw_key)
    assert digest != raw_key
    assert len(digest) == 64
    assert IntegrationService._credential_hash(raw_key) == digest


def test_canonical_hash_is_independent_of_json_key_order():
    first = {"event": "EVT-10", "stock": {"medicine": "MED-1", "quantity": 10}}
    second = {"stock": {"quantity": 10, "medicine": "MED-1"}, "event": "EVT-10"}
    assert canonical_snapshot_hash(first) == canonical_snapshot_hash(second)


def test_replay_accepts_identical_payload_hash_and_rejects_changed_content():
    digest = canonical_snapshot_hash({"event": "EVT-11", "quantity": 10})
    validate_replay_payload(digest, digest)
    changed = canonical_snapshot_hash({"event": "EVT-11", "quantity": 11})
    with pytest.raises(ValueError, match="different payload"):
        validate_replay_payload(digest, changed)


def test_snapshot_timestamp_must_be_newer_than_last_accepted_snapshot():
    now = datetime(2026, 10, 14, 10, 30, tzinfo=timezone.utc)
    last = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)

    validate_snapshot_timestamp(
        datetime(2026, 10, 14, 10, 1, tzinfo=timezone.utc),
        last,
        now,
    )
    with pytest.raises(ValueError, match="must be newer"):
        validate_snapshot_timestamp(last, last, now)
    with pytest.raises(ValueError, match="must be newer"):
        validate_snapshot_timestamp(
            datetime(2026, 10, 14, 9, 59, tzinfo=timezone.utc),
            last,
            now,
        )


def test_snapshot_timestamp_rejects_unreasonably_future_clock():
    now = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="future"):
        validate_snapshot_timestamp(
            now + timedelta(minutes=6),
            None,
            now,
        )


def test_snapshot_timestamp_rejects_naive_datetime():
    with pytest.raises(ValueError, match="timezone"):
        validate_snapshot_timestamp(
            datetime(2026, 10, 14, 10, 0),
            None,
            datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc),
        )
