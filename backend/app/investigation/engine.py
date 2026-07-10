from app.core.logging import log_ai_query
from app.investigation.contracts import (
    EntityExtractor,
    EvidenceRanker,
    RecommendationEngine,
    RetrievalProvider,
    RiskScorer,
    TimelineBuilder,
)
from collections.abc import Sequence

from app.investigation.dto import EvidenceCandidate, InvestigationQuery, InvestigationResponse, RetrievalResult
from app.investigation.evidence_ranking import WeightedEvidenceRanker
from app.investigation.formatter import StructuredInvestigationFormatter
from app.investigation.recommendations import RuleBasedRecommendationEngine
from app.investigation.retrieval import EmptyRetrievalProvider
from app.investigation.risk import WeightedRiskScorer
from app.investigation.timeline import EvidenceTimelineBuilder
from app.investigation.entity_extraction import EmptyEntityExtractor


class InvestigationEngine:
    """Coordinate the investigation pipeline without knowing business modules."""

    def __init__(
        self,
        entity_extractor: EntityExtractor | None = None,
        retrieval_provider: RetrievalProvider | None = None,
        evidence_ranker: EvidenceRanker | None = None,
        timeline_builder: TimelineBuilder | None = None,
        risk_scorer: RiskScorer | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        formatter: StructuredInvestigationFormatter | None = None,
    ) -> None:
        self.entity_extractor = entity_extractor or EmptyEntityExtractor()
        self.retrieval_provider = retrieval_provider or EmptyRetrievalProvider()
        self.evidence_ranker = evidence_ranker or WeightedEvidenceRanker()
        self.timeline_builder = timeline_builder or EvidenceTimelineBuilder()
        self.risk_scorer = risk_scorer or WeightedRiskScorer()
        self.recommendation_engine = recommendation_engine or RuleBasedRecommendationEngine()
        self.formatter = formatter or StructuredInvestigationFormatter()

    async def investigate(self, query: InvestigationQuery, request_id: str | None = None) -> InvestigationResponse:
        log_ai_query(query_type="investigation", user_id=query.requested_by, request_id=request_id)

        entities = await self.entity_extractor.extract(query)
        retrieval_results = await self.retrieval_provider.retrieve(query, entities)
        evidence = self._flatten_evidence(retrieval_results)
        ranked_evidence = await self.evidence_ranker.rank(query, evidence)
        timeline = await self.timeline_builder.build(ranked_evidence)
        risk = await self.risk_scorer.score(query, ranked_evidence, timeline)
        recommendations = await self.recommendation_engine.recommend(query, ranked_evidence, risk)

        return self.formatter.format(
            query=query,
            entities=entities,
            evidence=ranked_evidence,
            timeline=timeline,
            risk=risk,
            recommendations=recommendations,
        )

    def _flatten_evidence(self, retrieval_results: Sequence[RetrievalResult]) -> list[EvidenceCandidate]:
        return [item for result in retrieval_results for item in result.evidence]
