"""Deterministic stockout risk projection for reviewable decision support."""

from math import isfinite


def project_stockout(
    available_stock: int,
    reserved_stock: int,
    daily_consumption_rate: float,
    lead_time_days: int,
    safety_stock_days: int,
) -> dict:
    """Project days to stockout and replenishment risk from supplied inventory facts.

    In AegisFlow, available_stock is already the unreserved quantity. Reserved
    units are shown for transparency but must not be added to usable stock.
    This engine is rule-based, not a trained forecasting model.
    """
    if min(available_stock, reserved_stock, lead_time_days, safety_stock_days) < 0:
        raise ValueError("Stock, lead time and safety-stock values cannot be negative.")

    rate = float(daily_consumption_rate)
    if not isfinite(rate) or rate < 0:
        raise ValueError("Daily consumption must be a finite, non-negative value.")

    usable_stock = int(available_stock)
    if usable_stock == 0:
        return {
            "usable_stock": usable_stock,
            "projected_stockout_days": 0.0,
            "risk_score": 100.0,
            "risk_level": "CRITICAL",
            "recommended_action": "SOURCE_NETWORK",
            "explanation": "No unreserved stock is available; source eligible network stock immediately.",
        }

    if rate == 0:
        return {
            "usable_stock": usable_stock,
            "projected_stockout_days": None,
            "risk_score": None,
            "risk_level": "INSUFFICIENT_DATA",
            "recommended_action": "REVIEW_CONSUMPTION",
            "explanation": "A positive stockout projection requires a measured positive daily consumption rate.",
        }

    stockout_days = usable_stock / rate
    coverage_requirement_days = lead_time_days + safety_stock_days
    required_stock = rate * coverage_requirement_days
    risk_score = round(
        max(0.0, min(100.0, (1.0 - usable_stock / required_stock) * 100.0))
        if required_stock > 0
        else 0.0,
        2,
    )

    if stockout_days <= lead_time_days:
        risk_level = "CRITICAL"
        action = "SOURCE_NETWORK"
        explanation = (
            f"Projected stockout in {stockout_days:.2f} days, at or before the "
            f"{lead_time_days}-day replenishment lead time."
        )
    elif stockout_days <= coverage_requirement_days:
        risk_level = "HIGH" if risk_score >= 70 else "WARNING"
        action = "REPLENISH"
        explanation = (
            f"Projected stockout in {stockout_days:.2f} days, within lead time "
            f"plus the {safety_stock_days}-day safety-stock buffer."
        )
    elif risk_score >= 70:
        risk_level = "HIGH"
        action = "REPLENISH"
        explanation = "The stock buffer is materially below the configured replenishment-plus-safety requirement."
    elif risk_score >= 40:
        risk_level = "WARNING"
        action = "REVIEW_REPLENISHMENT"
        explanation = "Stock cover is above the immediate replenishment window but below the preferred buffer."
    else:
        risk_level = "SAFE"
        action = "MONITOR"
        explanation = "Recorded stock covers the configured replenishment lead time and safety-stock buffer."

    return {
        "usable_stock": usable_stock,
        "projected_stockout_days": round(stockout_days, 2),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommended_action": action,
        "explanation": explanation,
    }
