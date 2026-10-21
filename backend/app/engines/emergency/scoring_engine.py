from math import exp


class ScoringEngine:
    """Explainable deterministic scoring; scores are decision support, not ML probabilities."""

    DISTANCE_WEIGHT = 0.30
    INVENTORY_WEIGHT = 0.50
    DONOR_HEALTH_WEIGHT = 0.20

    @staticmethod
    def calculate_distance_score(distance_km: float) -> float:
        """Closer facility receives a higher score."""
        if distance_km < 0:
            raise ValueError("Distance cannot be negative.")
        return round(exp(-distance_km / 50), 4)

    @staticmethod
    def calculate_inventory_score(
        available_quantity: int,
        requested_quantity: int,
    ) -> float:
        """Score the portion of requested demand a single donor can cover."""
        if requested_quantity <= 0:
            return 0.0
        if available_quantity < 0:
            raise ValueError("Available quantity cannot be negative.")
        return round(min(available_quantity / requested_quantity, 1.0), 4)

    @staticmethod
    def calculate_donor_health_score(
        remaining_stock: int,
        minimum_threshold: int,
    ) -> float:
        """Score donor stock buffer above minimum stock, capped at 1.

        remaining_stock is current unreserved available stock. Eligibility is
        separately enforced by excluding donors whose transferable quantity is
        zero. A donor barely above its minimum should score lower than one with
        a meaningful surplus.
        """
        if remaining_stock < 0 or minimum_threshold < 0:
            raise ValueError("Stock values cannot be negative.")
        if minimum_threshold == 0:
            return 1.0 if remaining_stock > 0 else 0.0

        surplus = max(0, remaining_stock - minimum_threshold)
        return round(min(surplus / minimum_threshold, 1.0), 4)

    @classmethod
    def calculate_final_score(
        cls,
        distance_score: float,
        inventory_score: float,
        donor_health_score: float,
    ) -> float:
        components = (distance_score, inventory_score, donor_health_score)
        if any(score < 0 or score > 1 for score in components):
            raise ValueError("Scoring components must be between 0 and 1.")

        return round(
            (
                distance_score * cls.DISTANCE_WEIGHT
                + inventory_score * cls.INVENTORY_WEIGHT
                + donor_health_score * cls.DONOR_HEALTH_WEIGHT
            ) * 100,
            2,
        )
