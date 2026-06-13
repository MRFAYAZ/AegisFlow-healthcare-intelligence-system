class RankingEngine:

    """
    Responsible for:

    - candidate ranking
    - recommendation ordering
    """

    @staticmethod
    def rank_candidates(
        candidates: list
    ):

        return sorted(
            candidates,
            key=lambda candidate:
            candidate["ranking_score"],
            reverse=True
        )