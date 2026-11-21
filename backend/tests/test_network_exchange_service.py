from datetime import date, timedelta
from types import SimpleNamespace

from app.core.enums import BatchStatusEnum
from app.services.network_exchange_service import NetworkExchangeService


def make_inventory(
    *,
    cold_chain_required=False,
    cold_chain_capable=True,
    batches=None,
):
    return SimpleNamespace(
        available_stock=140,
        minimum_threshold=30,
        medicine=SimpleNamespace(cold_chain_required=cold_chain_required),
        facility=SimpleNamespace(cold_chain_capable=cold_chain_capable),
        batches=batches or [],
    )


def make_batch(quantity, expiry_date, status=BatchStatusEnum.AVAILABLE):
    return SimpleNamespace(
        quantity_available=quantity,
        expiry_date=expiry_date,
        status=status,
    )


def test_safe_transferable_quantity_respects_floor_expiry_and_batch_status():
    inventory = make_inventory(
        batches=[
            make_batch(80, date.today() + timedelta(days=10)),
            make_batch(30, date.today() - timedelta(days=1)),
            make_batch(20, date.today() + timedelta(days=30), BatchStatusEnum.QUARANTINED),
        ],
    )

    quantity, traceable, cold_chain_eligible = (
        NetworkExchangeService.safe_transferable_quantity(inventory, date.today())
    )

    assert quantity == 80
    assert traceable is True
    assert cold_chain_eligible is True


def test_cold_chain_stock_requires_capable_facility_and_batch_traceability():
    no_batches = make_inventory(cold_chain_required=True)
    incapable = make_inventory(
        cold_chain_required=True,
        cold_chain_capable=False,
        batches=[make_batch(100, date.today() + timedelta(days=30))],
    )

    assert NetworkExchangeService.safe_transferable_quantity(no_batches, date.today()) == (
        0,
        False,
        False,
    )
    assert NetworkExchangeService.safe_transferable_quantity(incapable, date.today()) == (
        0,
        True,
        False,
    )


def test_distance_km_uses_facility_coordinates():
    chennai = SimpleNamespace(latitude=13.0827, longitude=80.2707)
    nearby = SimpleNamespace(latitude=13.0674, longitude=80.2376)

    distance = NetworkExchangeService.distance_km(chennai, nearby)

    assert 3.5 < distance < 4.5