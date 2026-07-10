from collections.abc import Sequence
from typing import Protocol

from app.investigation.dto import (
    EvidenceCandidate,
    ExtractedEntity,
    InvestigationQuery,
    Recommendation,
    RetrievalResult,
    RiskAssessment,
    TimelineEvent,
)


class EntityExtractor(Protocol):
    async def extract(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        """Extract searchable entities from a free-form investigation query."""


class RetrievalProvider(Protocol):
    async def retrieve(
        self,
        query: InvestigationQuery,
        entities: Sequence[ExtractedEntity],
    ) -> Sequence[RetrievalResult]:
        """Retrieve normalized evidence candidates from business data sources."""


class EvidenceRanker(Protocol):
    async def rank(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
    ) -> Sequence[EvidenceCandidate]:
        """Rank evidence candidates by investigative relevance."""


class TimelineBuilder(Protocol):
    async def build(self, evidence: Sequence[EvidenceCandidate]) -> Sequence[TimelineEvent]:
        """Build a normalized chronological event sequence."""


class RiskScorer(Protocol):
    async def score(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        timeline: Sequence[TimelineEvent],
    ) -> RiskAssessment:
        """Score aggregate risk for an investigation response."""


class RecommendationEngine(Protocol):
    async def recommend(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        risk: RiskAssessment,
    ) -> Sequence[Recommendation]:
        """Produce operational recommendations."""


class AIProvider(Protocol):
    async def extract_entities(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        """AI-backed entity extraction boundary."""

    async def generate_recommendations(
        self,
        query: InvestigationQuery,
        evidence: Sequence[EvidenceCandidate],
        risk: RiskAssessment,
    ) -> Sequence[Recommendation]:
        """AI-backed recommendation boundary."""
