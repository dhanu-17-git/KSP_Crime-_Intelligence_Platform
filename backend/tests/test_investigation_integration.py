import pytest
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.investigation import _calculate_case_similarity, LocalRegexEntityExtractor
from app.investigation.dto import EntityType, ExtractedEntity, InvestigationQuery
from app.investigation.retrieval import PostgreSQLRetrievalProvider
from app.models.fir import Accused, CaseMaster, ComplainantDetails


def test_similarity_calculation_suspects_overlap():
    case_a = CaseMaster(case_master_id=1, accused=[], act_section_associations=[])
    case_b = CaseMaster(case_master_id=2, accused=[], act_section_associations=[])
    
    # Empty cases have 0 similarity
    assert _calculate_case_similarity(case_a, case_b) == 0.0

    # Overlapping suspects
    acc1_a = Accused(accused_name="Vikram Hegde")
    acc2_a = Accused(accused_name="Kiran Kumar")
    case_a.accused = [acc1_a, acc2_a]
    
    acc1_b = Accused(accused_name="Vikram Hegde")
    case_b.accused = [acc1_b]
    
    # suspects_a = {'Vikram Hegde', 'Kiran Kumar'}, suspects_b = {'Vikram Hegde'}
    # Intersection = 1, Union = 2 -> Jaccard = 0.5
    # Weighted score: 35% of 0.5 = 0.175 -> 17.5% similarity
    assert _calculate_case_similarity(case_a, case_b) == 17.5


@pytest.mark.asyncio
async def test_regex_extractor_parses_vehicles_and_cases():
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Mock known accused names dictionary lookup
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = ["Vikram Hegde", "Suresh Gowda"]
    mock_session.execute.return_value = mock_result

    extractor = LocalRegexEntityExtractor(mock_session)
    
    query = InvestigationQuery(
        query_text="Look up vehicle KA05MJ4421 and suspect Vikram Hegde in FIR 0142/2026",
        requested_by="test-officer"
    )
    
    entities = await extractor.extract(query)
    
    values = [e.value for e in entities]
    types = [e.entity_type for e in entities]
    
    assert "KA05MJ4421" in values
    assert EntityType.VEHICLE in types
    
    assert "FIR 0142/2026" in values
    assert EntityType.CASE in types

    assert "Vikram Hegde" in values
    assert EntityType.PERSON in types


@pytest.mark.asyncio
async def test_retrieval_provider_queries_correct_models():
    mock_session = AsyncMock(spec=AsyncSession)
    
    # Setup mock returns
    case = CaseMaster(
        case_master_id=10,
        crime_no="FIR 0142/2026",
        brief_facts="Armed heist of cargo with vehicle plate KA05MJ4421.",
        crime_registered_date=datetime(2026, 7, 6, tzinfo=UTC),
        latitude=Decimal("12.9345"),
        longitude=Decimal("77.6268"),
        gravity_offence_id=1,
        accused=[]
    )
    
    from unittest.mock import MagicMock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [case]
    mock_session.execute.return_value = mock_result
    
    provider = PostgreSQLRetrievalProvider(mock_session)
    entities = [
        ExtractedEntity(value="KA05MJ4421", entity_type=EntityType.VEHICLE, confidence=0.99)
    ]
    
    results = await provider.retrieve(
        InvestigationQuery(query_text="test", requested_by="officer"),
        entities
    )
    
    assert len(results) == 1
    assert results[0].source_name in ("postgres-ksp", "KSP Database")
    assert len(results[0].evidence) == 1
    assert results[0].evidence[0].id == "case-10"
    assert results[0].evidence[0].title == "FIR FIR 0142/2026"
    assert "KA05MJ4421" in results[0].evidence[0].summary
