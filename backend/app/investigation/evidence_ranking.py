from collections.abc import Sequence

from app.investigation.dto import EvidenceCandidate, InvestigationQuery


class WeightedEvidenceRanker:
    """Rank evidence by precomputed relevance, confidence, and risk weight."""

    def __init__(
        self,
        relevance_weight: float = 0.55,
        confidence_weight: float = 0.30,
        risk_weight: float = 0.15,
    ) -> None:
        self.relevance_weight = relevance_weight
        self.confidence_weight = confidence_weight
        self.risk_weight = risk_weight

    async def rank(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
    ) -> Sequence[EvidenceCandidate]:
        return sorted(evidence, key=self._score, reverse=True)

    def _score(self, evidence: EvidenceCandidate) -> float:
        return (
            evidence.relevance_score * self.relevance_weight
            + evidence.confidence * self.confidence_weight
            + evidence.risk_weight * self.risk_weight
        )
