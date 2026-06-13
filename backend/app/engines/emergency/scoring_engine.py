from math import exp


class ScoringEngine:

    """
    Core mathematical scoring engine.

    Responsible for:

    - distance scoring
    - inventory scoring
    - shortage protection scoring
    - weighted final score
    """

    DISTANCE_WEIGHT = 0.30
    INVENTORY_WEIGHT = 0.50
    DONOR_HEALTH_WEIGHT = 0.20

    @staticmethod
    def calculate_distance_score(
        distance_km: float
    ) -> float:

        """
        Closer facility = higher score
        """

        return round(
            exp(-distance_km / 50),
            4
        )

    @staticmethod
    def calculate_inventory_score(
        available_quantity: int,
        requested_quantity: int
    ) -> float:

        if requested_quantity <= 0:
            return 0

        score = (
            available_quantity
            / requested_quantity
        )

        return round(
            min(score, 1.0),
            4
        )

    @staticmethod
    def calculate_donor_health_score(
        remaining_stock: int,
        minimum_threshold: int
    ) -> float:

        if minimum_threshold <= 0:
            return 1.0

        ratio = (
            remaining_stock
            / minimum_threshold
        )

        return round(
            min(ratio, 1.0),
            4
        )

    @classmethod
    def calculate_final_score(
        cls,
        distance_score: float,
        inventory_score: float,
        donor_health_score: float
    ) -> float:

        final_score = (

            distance_score
            * cls.DISTANCE_WEIGHT

            +

            inventory_score
            * cls.INVENTORY_WEIGHT

            +

            donor_health_score
            * cls.DONOR_HEALTH_WEIGHT

        )

        return round(
            final_score * 100,
            2
        )