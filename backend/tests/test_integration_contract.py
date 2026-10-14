from datetime import date, datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.integration import (
    IntegrationBatchSnapshot,
    IntegrationInventoryItem,
    IntegrationInventorySnapshotRequest,
    IntegrationSourceCreate,
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

