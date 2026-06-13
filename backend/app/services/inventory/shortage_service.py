from app.core.enums import (
    SeverityEnum
)


class ShortageService:

    # =====================================================
    # CALCULATE SHORTAGE SCORE
    # =====================================================

    @staticmethod
    def calculate_shortage_score(
        available_stock: int,
        daily_consumption_rate: float,
        lead_time_days: int,
        safety_stock_days: int
    ) -> float:

        # ---------------------------------------------
        # PROJECTED CONSUMPTION
        # ---------------------------------------------

        projected_consumption = (
            daily_consumption_rate
            * lead_time_days
        )

        # ---------------------------------------------
        # SAFETY BUFFER
        # ---------------------------------------------

        safety_buffer = (
            daily_consumption_rate
            * safety_stock_days
        )

        # ---------------------------------------------
        # REQUIRED STOCK
        # ---------------------------------------------

        required_stock = (
            projected_consumption
            + safety_buffer
        )

        # ---------------------------------------------
        # STOCK SUFFICIENCY RATIO
        # ---------------------------------------------

        if required_stock <= 0:
            return 0.0

        stock_ratio = (
            available_stock
            / required_stock
        )

        # ---------------------------------------------
        # SHORTAGE SCORE
        # ---------------------------------------------

        shortage_score = (
            max(
                0,
                (1 - stock_ratio)
            ) * 100
        )

        return round(shortage_score, 2)

    # =====================================================
    # DETERMINE SEVERITY
    # =====================================================

    @staticmethod
    def determine_severity(
        shortage_score: float
    ) -> SeverityEnum:

        if shortage_score >= 90:
            return SeverityEnum.EMERGENCY

        if shortage_score >= 70:
            return SeverityEnum.CRITICAL

        if shortage_score >= 40:
            return SeverityEnum.WARNING

        return SeverityEnum.SAFE