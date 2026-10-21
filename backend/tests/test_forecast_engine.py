import pytest

from app.engines.inventory.forecast_engine import project_stockout


def test_projection_uses_unreserved_available_stock_and_computes_stockout_days():
    result = project_stockout(
        available_stock=100,
        reserved_stock=80,
        daily_consumption_rate=25,
        lead_time_days=3,
        safety_stock_days=2,
    )
    assert result["usable_stock"] == 100
    assert result["projected_stockout_days"] == 4.0
    assert result["risk_level"] == "WARNING"
    assert result["recommended_action"] == "REPLENISH"


def test_zero_stock_is_critical_even_when_consumption_is_unknown():
    result = project_stockout(0, 0, 0, 4, 3)
    assert result["risk_level"] == "CRITICAL"
    assert result["risk_score"] == 100
    assert result["recommended_action"] == "SOURCE_NETWORK"


def test_unknown_consumption_is_not_misreported_as_safe():
    result = project_stockout(120, 20, 0, 5, 3)
    assert result["projected_stockout_days"] is None
    assert result["risk_score"] is None
    assert result["risk_level"] == "INSUFFICIENT_DATA"
    assert result["recommended_action"] == "REVIEW_CONSUMPTION"


def test_stockout_before_lead_time_recommends_network_sourcing():
    result = project_stockout(20, 0, 10, 5, 3)
    assert result["projected_stockout_days"] == 2.0
    assert result["risk_level"] == "CRITICAL"
    assert result["recommended_action"] == "SOURCE_NETWORK"


@pytest.mark.parametrize(
    "args",
    [
        (-1, 0, 1, 3, 2),
        (10, -1, 1, 3, 2),
        (10, 0, -1, 3, 2),
        (10, 0, 1, -3, 2),
        (10, 0, 1, 3, -2),
    ],
)
def test_invalid_forecast_inputs_are_rejected(args):
    with pytest.raises(ValueError):
        project_stockout(*args)
