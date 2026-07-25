from collections.abc import Sequence
import logging

from app.investigation.contracts import AIProvider
from app.investigation.dto import ExtractedEntity, InvestigationQuery


logger = logging.getLogger(__name__)


class ProviderEntityExtractor:
    """Entity extractor that delegates NLP work to a swappable AI provider."""

    def __init__(self, ai_provider: AIProvider, fallback_extractor: object | None = None) -> None:
        self.ai_provider = ai_provider
        self.fallback_extractor = fallback_extractor

    async def extract(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        try:
            return await self.ai_provider.extract_entities(query)
        except Exception as exc:
            if self.fallback_extractor is None:
                raise

            logger.warning(
                "Gemini entity extraction failed; using fallback extractor",
                extra={
                    "details": {
                        "query_text": query.query_text,
                        "error": str(exc),
                    }
                },
            )
            return await self.fallback_extractor.extract(query)


class EmptyEntityExtractor:
    """Safe fallback extractor used until an AI provider is configured."""

    async def extract(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        return []
