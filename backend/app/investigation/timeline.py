from collections.abc import Sequence

from app.investigation.dto import EvidenceCandidate, TimelineEvent


class EvidenceTimelineBuilder:
    """Build chronological events from dated evidence candidates."""

    async def build(self, evidence: Sequence[EvidenceCandidate]) -> Sequence[TimelineEvent]:
        events = [
            TimelineEvent(
                title=item.title,
                occurred_at=item.occurred_at,
                description=item.summary,
                evidence_ids=[item.id],
                confidence=item.confidence,
            )
            for item in evidence
            if item.occurred_at is not None
        ]
        return sorted(events, key=lambda event: event.occurred_at)
