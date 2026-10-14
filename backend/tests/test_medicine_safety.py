from dataclasses import dataclass
from datetime import date

import pytest

from app.engines.inventory.medicine_safety import (
    plan_fefo_reservation,
    safe_transferable_quantity,
)


@dataclass
class Lot:
    batch_id: str
    expiry_date: date
    quantity_available: int


def test_safe_quantity_is_bounded_by_stock_surplus_and_verified_lots():
    assert safe_transferable_quantity(100, 20, 35) == 35
    assert safe_transferable_quantity(30, 20, 50) == 10
    assert safe_transferable_quantity(20, 20, 50) == 0


def test_fefo_reserves_earliest_expiry_first_and_skips_expired_batches():
    today = date(2026, 10, 14)
    batches = [
        Lot("later", date(2027, 7, 1), 80),
        Lot("expired", date(2026, 10, 13), 50),
        Lot("earliest", date(2026, 12, 1), 12),
    ]

    plan = plan_fefo_reservation(batches, 20, as_of=today)

    assert [(batch.batch_id, quantity) for batch, quantity in plan] == [
        ("earliest", 12),
        ("later", 8),
    ]
    # Planning is side-effect free; the database transaction performs mutations.
    assert batches[0].quantity_available == 80


def test_fefo_fails_closed_when_unexpired_batches_do_not_cover_request():
    batches = [Lot("expiring", date(2026, 12, 1), 2)]
    with pytest.raises(ValueError, match="Insufficient unexpired batch stock"):
        plan_fefo_reservation(batches, 3, as_of=date(2026, 10, 14))


def test_invalid_safe_stock_values_are_rejected():
    with pytest.raises(ValueError):
        safe_transferable_quantity(10, 5, -1)
