from app.engines.emergency.scoring_engine import (
    ScoringEngine
)

from app.engines.emergency.ranking_engine import (
    RankingEngine
)


class MatchingEngine:

    """
    Emergency matching engine.

    Finds best medicine sources.
    """

    @staticmethod
    def generate_matches(
        candidates: list,
        requested_quantity: int
    ):

        ranked_candidates = []

        for candidate in candidates:

            distance_score = (
                ScoringEngine
                .calculate_distance_score(
                    candidate["distance_km"]
                )
            )

            inventory_score = (
                ScoringEngine
                .calculate_inventory_score(
                    candidate["available_quantity"],
                    requested_quantity
                )
            )

            donor_health_score = (
                ScoringEngine
                .calculate_donor_health_score(
                    candidate["remaining_stock"],
                    candidate["minimum_threshold"]
                )
            )

            final_score = (
                ScoringEngine
                .calculate_final_score(
                    distance_score,
                    inventory_score,
                    donor_health_score
                )
            )

            candidate[
                "ranking_score"
            ] = final_score

            ranked_candidates.append(
                candidate
            )

        return (
            RankingEngine
            .rank_candidates(
                ranked_candidates
            )
        )