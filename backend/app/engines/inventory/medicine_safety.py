"""Hard safety gates and FEFO allocation helpers for medicine lot handling."""

from datetime import date
from typing import Iterable, Any


def safe_transferable_quantity(
    aggregate_available_stock: int,
    minimum_threshold: int,
    unexpired_batch_available: int,
) -> int:
    """Return quantity protected by both stock threshold and verified lots."""
    if min(aggregate_available_stock, minimum_threshold, unexpired_batch_available) < 0:
        raise ValueError("Stock quantities cannot be negative.")
    stock_surplus = max(0, aggregate_available_stock - minimum_threshold)
    return min(stock_surplus, unexpired_batch_available)


def plan_fefo_reservation(
    batches: Iterable[Any],
    requested_quantity: int,
    as_of: date | None = None,
) -> list[tuple[Any, int]]:
    """Plan a First-Expiry-First-Out reservation without mutating supplied rows.

    Each batch must expose batch_id, expiry_date, and quantity_available.
    Returned quantities cover the exact request or a ValueError is raised.
    The caller applies the plan inside its locked database transaction.
    """
    if requested_quantity <= 0:
        raise ValueError("Requested quantity must be greater than zero.")

    today = as_of or date.today()
    eligible = []
    for batch in batches:
        expiry = batch.expiry_date
        quantity = int(batch.quantity_available or 0)
        if expiry is not None and expiry >= today and quantity > 0:
            eligible.append(batch)

    eligible.sort(key=lambda batch: (batch.expiry_date, str(batch.batch_id)))
    available = sum(int(batch.quantity_available or 0) for batch in eligible)
    if available < requested_quantity:
        raise ValueError(
            f"Insufficient unexpired batch stock: {available} available, "
            f"{requested_quantity} requested."
        )

    remaining = requested_quantity
    plan: list[tuple[Any, int]] = []
    for batch in eligible:
        if remaining == 0:
            break
        quantity = min(remaining, int(batch.quantity_available or 0))
        plan.append((batch, quantity))
        remaining -= quantity

    if remaining:
        raise ValueError("FEFO reservation plan could not cover the requested quantity.")
    return plan
