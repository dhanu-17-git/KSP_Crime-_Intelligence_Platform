from collections.abc import Sequence

from app.investigation.contracts import AIProvider
from app.investigation.dto import (
    EvidenceCandidate,
    InvestigationQuery,
    Recommendation,
    RecommendationPriority,
    RiskAssessment,
    RiskLevel,
)


class ProviderRecommendationEngine:
    """Recommendation engine that delegates text generation to an AI provider."""

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai_provider = ai_provider

    async def recommend(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        risk: RiskAssessment,
    ) -> Sequence[Recommendation]:
        return await self.ai_provider.generate_recommendations(query, evidence, risk)


class RuleBasedRecommendationEngine:
    """Deterministic fallback recommendations for foundation-level use."""

    async def recommend(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        risk: RiskAssessment,
    ) -> Sequence[Recommendation]:
        if risk.level in {RiskLevel.CRITICAL, RiskLevel.HIGH}:
            return [
                Recommendation(
                    title="Prioritize immediate supervisory review",
                    description="Escalate the investigation summary to the authorized supervisory officer.",
                    priority=RecommendationPriority.URGENT if risk.level == RiskLevel.CRITICAL else RecommendationPriority.HIGH,
                    rationale="Risk score crossed the high-risk operational threshold.",
                    related_evidence_ids=[item.id for item in evidence[:5]],
                )
            ]

        return [
            Recommendation(
                title="Continue evidence enrichment",
                description="Collect additional corroborating evidence before operational escalation.",
                priority=RecommendationPriority.MEDIUM,
                rationale="Current risk score does not yet justify emergency escalation.",
                related_evidence_ids=[item.id for item in evidence[:3]],
            )
        ]
