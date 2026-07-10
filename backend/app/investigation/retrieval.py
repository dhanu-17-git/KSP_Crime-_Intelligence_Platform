from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.investigation.dto import (
    EntityType,
    EvidenceCandidate,
    EvidenceType,
    ExtractedEntity,
    InvestigationQuery,
    RetrievalResult,
)
from app.models.fir import Accused, CaseMaster, ComplainantDetails
from app.utils.phonetic import phonetic_hash


class PostgreSQLRetrievalProvider:
    """Production-grade retrieval provider querying KSP PostgreSQL schema."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def retrieve(
        self,
        query: InvestigationQuery,
        entities: Sequence[ExtractedEntity],
    ) -> Sequence[RetrievalResult]:
        results: list[RetrievalResult] = []

        if not entities:
            # Fallback search using query text if no entities extracted
            fallback_entities = [
                ExtractedEntity(value=query.query_text, entity_type=EntityType.UNKNOWN, confidence=0.5)
            ]
            entities = fallback_entities

        for entity in entities:
            evidence_candidates: list[EvidenceCandidate] = []
            
            # Retrieve depending on entity types
            if entity.entity_type == EntityType.VEHICLE:
                candidates = await self._retrieve_by_vehicle(entity.value)
                evidence_candidates.extend(candidates)
                
            elif entity.entity_type == EntityType.PERSON:
                candidates = await self._retrieve_by_person_phonetic(entity.value)
                evidence_candidates.extend(candidates)
                
            elif entity.entity_type == EntityType.CASE:
                candidates = await self._retrieve_by_case(entity.value)
                evidence_candidates.extend(candidates)
                
            else:
                # Default text match across brief_facts
                candidates = await self._retrieve_by_text(entity.value)
                evidence_candidates.extend(candidates)

            if evidence_candidates:
                results.append(
                    RetrievalResult(
                        source_name="postgres-ksp",
                        evidence=evidence_candidates,
                        metadata={"entity_value": entity.value, "entity_type": entity.entity_type},
                    )
                )

        return results

    async def _retrieve_by_vehicle(self, plate: str) -> list[EvidenceCandidate]:
        candidates: list[EvidenceCandidate] = []
        stmt = (
            select(CaseMaster)
            .where(CaseMaster.brief_facts.ilike(f"%{plate}%"))
            .options(
                selectinload(CaseMaster.accused),
                selectinload(CaseMaster.crime_major_head),
                selectinload(CaseMaster.crime_minor_head),
            )
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        for case in cases:
            occurred_dt = self._normalize_datetime(case.incident_from_date or case.crime_registered_date)
            candidates.append(
                EvidenceCandidate(
                    id=f"case-{case.case_master_id}",
                    evidence_type=EvidenceType.FIR,
                    title=f"FIR {case.crime_no or case.case_no or case.case_master_id}",
                    summary=case.brief_facts or "No details available",
                    occurred_at=occurred_dt,
                    source="postgres-ksp",
                    confidence=0.95,
                    relevance_score=0.9,
                    risk_weight=0.8 if case.gravity_offence_id == 1 else 0.5,
                    metadata={
                        "latitude": float(case.latitude) if case.latitude else None,
                        "longitude": float(case.longitude) if case.longitude else None,
                        "crime_group": case.crime_major_head.crime_group_name if case.crime_major_head else None,
                        "accused_names": [acc.accused_name for acc in case.accused],
                    },
                )
            )
        return candidates

    async def _retrieve_by_person_phonetic(self, name: str) -> list[EvidenceCandidate]:
        candidates: list[EvidenceCandidate] = []
        target_hash = phonetic_hash(name)
        if not target_hash:
            return candidates

        # Query all Accused records (for datathon scale we load and match phonetically in Python)
        # In larger production datasets, precomputed phonetic columns are used
        stmt = select(Accused).options(selectinload(Accused.case))
        result = await self.session.execute(stmt)
        all_accused = result.scalars().all()

        for acc in all_accused:
            if phonetic_hash(acc.accused_name) == target_hash:
                candidates.append(
                    EvidenceCandidate(
                        id=f"suspect-{acc.accused_master_id}",
                        evidence_type=EvidenceType.SUSPECT,
                        title=f"Accused: {acc.accused_name}",
                        summary=f"Accused in Case ID: {acc.case_master_id}. Person ID: {acc.person_id or 'N/A'}, Age: {acc.age_year or 'N/A'}",
                        occurred_at=None,
                        source="postgres-ksp",
                        confidence=1.0,
                        relevance_score=1.0,
                        risk_weight=0.9,
                        metadata={
                            "name": acc.accused_name,
                            "person_id": acc.person_id,
                            "case_master_id": acc.case_master_id,
                        },
                    )
                )

        # Also search complainants
        stmt_comp = select(ComplainantDetails).options(selectinload(ComplainantDetails.case))
        result_comp = await self.session.execute(stmt_comp)
        all_comps = result_comp.scalars().all()

        for comp in all_comps:
            if phonetic_hash(comp.complainant_name) == target_hash:
                candidates.append(
                    EvidenceCandidate(
                        id=f"complainant-{comp.complainant_id}",
                        evidence_type=EvidenceType.DOCUMENT,
                        title=f"Complainant: {comp.complainant_name}",
                        summary=f"Complainant in Case ID: {comp.case_master_id}. Age: {comp.age_year or 'N/A'}",
                        occurred_at=None,
                        source="postgres-ksp",
                        confidence=0.85,
                        relevance_score=0.7,
                        risk_weight=0.3,
                        metadata={
                            "name": comp.complainant_name,
                            "case_master_id": comp.case_master_id,
                        },
                    )
                )

        return candidates

    async def _retrieve_by_case(self, case_key: str) -> list[EvidenceCandidate]:
        candidates: list[EvidenceCandidate] = []
        stmt = (
            select(CaseMaster)
            .where(
                (CaseMaster.crime_no.ilike(f"%{case_key}%")) | 
                (CaseMaster.case_no.ilike(f"%{case_key}%"))
            )
            .options(
                selectinload(CaseMaster.accused),
                selectinload(CaseMaster.crime_major_head),
            )
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        for case in cases:
            occurred_dt = self._normalize_datetime(case.incident_from_date or case.crime_registered_date)
            candidates.append(
                EvidenceCandidate(
                    id=f"case-{case.case_master_id}",
                    evidence_type=EvidenceType.FIR,
                    title=f"FIR {case.crime_no or case.case_no or case.case_master_id}",
                    summary=case.brief_facts or "No details available",
                    occurred_at=occurred_dt,
                    source="postgres-ksp",
                    confidence=1.0,
                    relevance_score=1.0,
                    risk_weight=0.7,
                    metadata={
                        "latitude": float(case.latitude) if case.latitude else None,
                        "longitude": float(case.longitude) if case.longitude else None,
                        "crime_group": case.crime_major_head.crime_group_name if case.crime_major_head else None,
                    },
                )
            )
        return candidates

    async def _retrieve_by_text(self, text: str) -> list[EvidenceCandidate]:
        candidates: list[EvidenceCandidate] = []
        if len(text) < 3:
            return candidates

        stmt = (
            select(CaseMaster)
            .where(CaseMaster.brief_facts.ilike(f"%{text}%"))
            .options(selectinload(CaseMaster.accused))
            .limit(10)
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        for case in cases:
            occurred_dt = self._normalize_datetime(case.incident_from_date or case.crime_registered_date)
            candidates.append(
                EvidenceCandidate(
                    id=f"case-{case.case_master_id}",
                    evidence_type=EvidenceType.FIR,
                    title=f"FIR {case.crime_no or case.case_no or case.case_master_id}",
                    summary=case.brief_facts or "No details available",
                    occurred_at=occurred_dt,
                    source="postgres-ksp",
                    confidence=0.8,
                    relevance_score=0.6,
                    risk_weight=0.5,
                    metadata={},
                )
            )
        return candidates

    def _normalize_datetime(self, val: Any) -> datetime | None:
        if isinstance(val, datetime):
            if val.tzinfo is None:
                return val.replace(tzinfo=UTC)
            return val
        if isinstance(val, (str, bytes)):
            try:
                dt = datetime.fromisoformat(val)
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=UTC)
                return dt
            except ValueError:
                return None
        return None


class EmptyRetrievalProvider:
    """Retrieval placeholder until business modules expose data sources."""

    async def retrieve(
        self,
        query: InvestigationQuery,
        entities: Sequence[ExtractedEntity],
    ) -> Sequence[RetrievalResult]:
        return []

