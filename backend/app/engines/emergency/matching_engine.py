from app.engines.emergency.scoring_engine import ScoringEngine
from app.engines.emergency.ranking_engine import RankingEngine


class MatchingEngine:
    """Explainable deterministic ranking for emergency medicine sourcing."""

    @staticmethod
    def generate_matches(candidates: list, requested_quantity: int) -> list[dict]:
        if requested_quantity <= 0:
            raise ValueError("Requested quantity must be greater than zero.")

        ranked_candidates = []
        for original in candidates:
            candidate = dict(original)
            distance_score = ScoringEngine.calculate_distance_score(
                float(candidate["distance_km"])
            )
            inventory_score = ScoringEngine.calculate_inventory_score(
                int(candidate.get("transferable_quantity", candidate["available_quantity"])),
                requested_quantity,
            )
            donor_health_score = ScoringEngine.calculate_donor_health_score(
                int(candidate["remaining_stock"]),
                int(candidate["minimum_threshold"]),
            )

            candidate["ranking_score"] = ScoringEngine.calculate_final_score(
                distance_score, inventory_score, donor_health_score
            )
            candidate["score_breakdown"] = {
                "distance_score": distance_score,
                "inventory_score": inventory_score,
                "donor_health_score": donor_health_score,
                "distance_weight": ScoringEngine.DISTANCE_WEIGHT,
                "inventory_weight": ScoringEngine.INVENTORY_WEIGHT,
                "donor_health_weight": ScoringEngine.DONOR_HEALTH_WEIGHT,
            }
            candidate["suggested_quantity"] = min(
                int(candidate.get("transferable_quantity", candidate["available_quantity"])),
                requested_quantity,
            )
            ranked_candidates.append(candidate)

        ranked = RankingEngine.rank_candidates(ranked_candidates)
        for rank, candidate in enumerate(ranked, start=1):
            candidate["rank"] = rank
            candidate["recommendation_reason"] = (
                f"Ranked #{rank}: {candidate.get('distance_km', 0):.2f} km away; "
                f"{candidate.get('transferable_quantity', candidate['available_quantity'])} "
                f"units safely transferable against a {requested_quantity}-unit request; "
                f"weighted match score {candidate['ranking_score']:.2f}/100."
            )
        return ranked
