from collections.abc import Sequence
from datetime import UTC, datetime

from app.investigation.dto import (
    EvidenceCandidate,
    ExtractedEntity,
    InvestigationQuery,
    InvestigationResponse,
    Recommendation,
    RiskAssessment,
    TimelineEvent,
)


class StructuredInvestigationFormatter:
    """Create the stable response object consumed by future API routes."""

    def format(
        self,
        query: InvestigationQuery,
        entities: Sequence[ExtractedEntity],
        evidence: Sequence[EvidenceCandidate],
        timeline: Sequence[TimelineEvent],
        risk: RiskAssessment,
        recommendations: Sequence[Recommendation],
        *,
        thread_id: str = "",
        is_follow_up: bool = False,
        report_text: str = "",
    ) -> InvestigationResponse:
        has_data = len(evidence) > 0
        status = "success" if has_data else "insufficient_data"

        return InvestigationResponse(
            thread_id=thread_id,
            is_follow_up=is_follow_up,
            status=status,
            query=query,
            entities=list(entities),
            evidence=list(evidence),
            timeline=list(timeline),
            risk=risk,
            recommendations=list(recommendations),
            report_text=report_text,
            metadata={"generated_at": datetime.now(UTC).isoformat()},
        )
