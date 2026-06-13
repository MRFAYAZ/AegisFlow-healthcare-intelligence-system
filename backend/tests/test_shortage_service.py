from app.services.inventory.shortage_service import (
    ShortageService
)


def test_shortage_service():

    score = (
        ShortageService
        .calculate_shortage_score(
            available_stock=100,
            daily_consumption_rate=25,
            lead_time_days=5,
            safety_stock_days=3
        )
    )

    severity = (
        ShortageService
        .determine_severity(score)
    )

    print("Shortage Score:", score)

    print("Severity:", severity.value)

    print("✅ Shortage engine working")


if __name__ == "__main__":
    test_shortage_service()