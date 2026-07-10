from datetime import UTC, datetime

import pytest

from app.investigation.dto import (
    EntityType,
    EvidenceCandidate,
    EvidenceType,
    ExtractedEntity,
    InvestigationQuery,
    RetrievalResult,
    RiskLevel,
)
from app.investigation.engine import InvestigationEngine
from app.investigation.providers.gemini import GeminiAIProvider, GeminiProviderNotConfiguredError


class StubExtractor:
    async def extract(self, query):
        return [ExtractedEntity(value="KA05MJ4421", entity_type=EntityType.VEHICLE, confidence=0.98)]


class StubRetrievalProvider:
    async def retrieve(self, query, entities):
        return [
            RetrievalResult(
                source_name="test-source",
                evidence=[
                    EvidenceCandidate(
                        id="ev-low",
                        evidence_type=EvidenceType.DOCUMENT,
                        title="Low relevance item",
                        summary="Background document",
                        occurred_at=datetime(2026, 7, 5, tzinfo=UTC),
                        source="fixture",
                        confidence=0.5,
                        relevance_score=0.2,
                        risk_weight=0.1,
                    ),
                    EvidenceCandidate(
                        id="ev-high",
                        evidence_type=EvidenceType.VEHICLE,
                        title="High relevance vehicle hit",
                        summary="Vehicle appears near a high-risk event",
                        occurred_at=datetime(2026, 7, 6, tzinfo=UTC),
                        source="fixture",
                        confidence=0.95,
                        relevance_score=0.9,
                        risk_weight=0.9,
                    ),
                ],
            )
        ]


@pytest.mark.asyncio
async def test_investigation_engine_orchestrates_pipeline():
    engine = InvestigationEngine(
        entity_extractor=StubExtractor(),
        retrieval_provider=StubRetrievalProvider(),
    )

    response = await engine.investigate(
        InvestigationQuery(query_text="Find vehicle KA05MJ4421", requested_by="officer-1"),
        request_id="req-1",
    )

    assert response.entities[0].value == "KA05MJ4421"
    assert [item.id for item in response.evidence] == ["ev-high", "ev-low"]
    assert [item.evidence_ids[0] for item in response.timeline] == ["ev-low", "ev-high"]
    assert response.risk.level == RiskLevel.MEDIUM
    assert response.recommendations
    assert response.metadata["generated_at"]


@pytest.mark.asyncio
async def test_default_engine_returns_empty_low_risk_response():
    engine = InvestigationEngine()

    response = await engine.investigate(InvestigationQuery(query_text="unknown", requested_by="officer-1"))

    assert response.entities == []
    assert response.evidence == []
    assert response.timeline == []
    assert response.risk.level == RiskLevel.LOW
    assert response.risk.score == 0


@pytest.mark.asyncio
async def test_gemini_provider_is_isolated_and_not_configured_by_default():
    provider = GeminiAIProvider()

    with pytest.raises(GeminiProviderNotConfiguredError):
        await provider.extract_entities(InvestigationQuery(query_text="test", requested_by="officer-1"))
