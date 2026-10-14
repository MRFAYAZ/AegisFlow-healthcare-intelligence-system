import pytest

from app.engines.emergency.geo import haversine_km
from app.engines.emergency.matching_engine import MatchingEngine


def test_haversine_same_point_is_zero():
    assert haversine_km(13.0827, 80.2707, 13.0827, 80.2707) == pytest.approx(0)


def test_haversine_chennai_to_bengaluru_is_plausible():
    distance = haversine_km(13.0827, 80.2707, 12.9716, 77.5946)
    assert 280 < distance < 310


@pytest.mark.parametrize(
    "coordinates",
    [
        (91, 0, 0, 0),
        (0, 181, 0, 0),
        (-91, 0, 0, 0),
    ],
)
def test_haversine_rejects_invalid_coordinates(coordinates):
    with pytest.raises(ValueError):
        haversine_km(*coordinates)


def test_matching_ranks_closer_equally_capable_source_higher_and_explains_it():
    candidates = [
        {
            "facility_id": "far",
            "available_quantity": 100,
            "transferable_quantity": 100,
            "remaining_stock": 120,
            "minimum_threshold": 20,
            "distance_km": 20.0,
        },
        {
            "facility_id": "near",
            "available_quantity": 100,
            "transferable_quantity": 100,
            "remaining_stock": 120,
            "minimum_threshold": 20,
            "distance_km": 2.0,
        },
    ]

    ranked = MatchingEngine.generate_matches(candidates, requested_quantity=80)

    assert ranked[0]["facility_id"] == "near"
    assert ranked[0]["suggested_quantity"] == 80
    assert ranked[0]["rank"] == 1
    assert ranked[0]["recommendation_reason"]
    assert set(ranked[0]["score_breakdown"]) == {
        "distance_score",
        "inventory_score",
        "donor_health_score",
        "distance_weight",
        "inventory_weight",
        "donor_health_weight",
    }
