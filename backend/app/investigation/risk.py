from collections.abc import Sequence

from app.investigation.dto import EvidenceCandidate, InvestigationQuery, RiskAssessment, RiskLevel, TimelineEvent


class WeightedRiskScorer:
    """Compute a bounded risk assessment from ranked evidence."""

    async def score(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        timeline: Sequence[TimelineEvent],
    ) -> RiskAssessment:
        if not evidence:
            return RiskAssessment(score=0, level=RiskLevel.LOW, factors=["No evidence available"])

        weighted_score = sum(item.risk_weight * item.confidence for item in evidence) / len(evidence)
        chronology_boost = min(len(timeline) * 3, 15)
        score = min(round(weighted_score * 100 + chronology_boost), 100)

        factors = [
            f"{item.title} ({item.evidence_type.value})"
            for item in sorted(evidence, key=lambda candidate: candidate.risk_weight, reverse=True)[:3]
            if item.risk_weight > 0
        ]

        return RiskAssessment(score=score, level=self._level(score), factors=factors)

    def _level(self, score: int) -> RiskLevel:
        if score >= 80:
            return RiskLevel.CRITICAL
        if score >= 60:
            return RiskLevel.HIGH
        if score >= 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
