from collections.abc import Sequence

from app.investigation.contracts import AIProvider
from app.investigation.dto import ExtractedEntity, InvestigationQuery


class ProviderEntityExtractor:
    """Entity extractor that delegates NLP work to a swappable AI provider."""

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai_provider = ai_provider

    async def extract(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        return await self.ai_provider.extract_entities(query)


class EmptyEntityExtractor:
    """Safe fallback extractor used until an AI provider is configured."""

    async def extract(self, query: InvestigationQuery) -> Sequence[ExtractedEntity]:
        return []
