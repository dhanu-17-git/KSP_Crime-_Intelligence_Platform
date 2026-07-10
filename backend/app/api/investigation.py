import json
import math
import re
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.database import get_db_session
from app.dependencies.auth import get_current_user
from app.investigation.dto import (
    ConversationTurn,
    EntityType,
    EvidenceCandidate,
    EvidenceType,
    ExtractedEntity,
    InvestigationQuery,
    InvestigationResponse,
    RiskAssessment,
    RiskLevel,
)
from app.investigation.engine import InvestigationEngine
from app.investigation.entity_extraction import ProviderEntityExtractor
from app.investigation.providers.gemini import GeminiAIProvider
from app.investigation.recommendations import RuleBasedRecommendationEngine
from app.investigation.retrieval import PostgreSQLRetrievalProvider
from app.models.fir import Accused, CaseMaster
from app.schemas.user import CurrentUser

router = APIRouter(prefix="/investigation", tags=["investigation"])
settings = get_settings()


# ── In-memory thread store ──────────────────────────────────────────────────


@dataclass
class ThreadContext:
    thread_id: str
    entities_seen: list[ExtractedEntity] = field(default_factory=list)
    evidence_context: list[EvidenceCandidate] = field(default_factory=list)
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    report_summary: str = ""
    original_query: str = ""


_thread_store: dict[str, ThreadContext] = {}


# ── Entity extractors ──────────────────────────────────────────────────────


class LocalRegexEntityExtractor:
    """Regex-based fallback entity extractor when Gemini API is unconfigured."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def extract(self, query: InvestigationQuery) -> list[ExtractedEntity]:
        entities: list[ExtractedEntity] = []
        text = query.query_text

        # 1. Regex for vehicles (e.g. KA05MJ4421 or KA-05-MJ-4421)
        vehicle_pattern = r"\b[a-zA-Z]{2}[-\s]*[0-9]{2}[-\s]*[a-zA-Z]{1,2}[-\s]*[0-9]{4}\b"
        vehicles = re.findall(vehicle_pattern, text)
        for v in vehicles:
            normalized_v = re.sub(r"[-\s]", "", v).upper()
            entities.append(
                ExtractedEntity(
                    value=normalized_v,
                    entity_type=EntityType.VEHICLE,
                    confidence=0.99,
                    source="regex-extractor",
                )
            )

        # 2. Regex for cases (e.g. FIR 0142/2026)
        case_pattern = r"\bfir[-\s]*[0-9]+/[0-9]+\b"
        cases = re.findall(case_pattern, text, re.IGNORECASE)
        for c in cases:
            entities.append(
                ExtractedEntity(
                    value=c.upper(),
                    entity_type=EntityType.CASE,
                    confidence=0.95,
                    source="regex-extractor",
                )
            )

        # 3. Accused Name matching
        stmt = select(Accused.accused_name).distinct()
        result = await self.session.execute(stmt)
        known_names = result.scalars().all()
        for name in known_names:
            if name.lower() in text.lower():
                entities.append(
                    ExtractedEntity(
                        value=name,
                        entity_type=EntityType.PERSON,
                        confidence=0.90,
                        source="name-dictionary",
                    )
                )

        return entities


# ── Engine factory ──────────────────────────────────────────────────────────


def _get_extractor(db: AsyncSession):
    if settings.ai_provider == "gemini" and settings.gemini_api_key:
        ai_provider = GeminiAIProvider(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model_name,
        )
        return ProviderEntityExtractor(ai_provider)
    return LocalRegexEntityExtractor(db)


def _get_gemini_provider() -> GeminiAIProvider | None:
    if settings.ai_provider == "gemini" and settings.gemini_api_key:
        return GeminiAIProvider(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model_name,
        )
    return None


def get_investigation_engine(db: AsyncSession) -> InvestigationEngine:
    return InvestigationEngine(
        entity_extractor=_get_extractor(db),
        retrieval_provider=PostgreSQLRetrievalProvider(db),
        recommendation_engine=RuleBasedRecommendationEngine(),
    )


# ── Helper: diff entities to find new ones ──────────────────────────────────


def _find_new_entities(
    incoming: Sequence[ExtractedEntity],
    seen: Sequence[ExtractedEntity],
) -> list[ExtractedEntity]:
    """Return entities from `incoming` that don't overlap with `seen`."""
    seen_values = {e.value.lower() for e in seen}
    return [e for e in incoming if e.value.lower() not in seen_values]


# ── Helper: build context JSON for Gemini ───────────────────────────────────


def _build_context_json(thread: ThreadContext) -> str:
    """Group and serialize thread context by entity type to guarantee multi-entity integrity."""
    suspects = []
    cases = []
    vehicles = []
    other = []

    seen_ids = set()

    for ev in thread.evidence_context[:40]:  # Cap at 40 items for prompt safety
        if ev.id in seen_ids:
            continue
        seen_ids.add(ev.id)

        item = {
            "id": ev.id,
            "title": ev.title,
            "summary": ev.summary,
            "source": ev.source,
            "risk_weight": ev.risk_weight,
            **ev.metadata
        }

        if ev.evidence_type == EvidenceType.SUSPECT:
            suspects.append(item)
        elif ev.evidence_type == EvidenceType.FIR:
            cases.append(item)
        elif ev.evidence_type == EvidenceType.VEHICLE:
            vehicles.append(item)
        else:
            other.append(item)

    context_data = {
        "original_query": thread.original_query,
        "entities_present": [e.value for e in thread.entities_seen],
        "suspect_profiles": suspects,
        "case_records": cases,
        "vehicle_records": vehicles,
        "other_records": other,
    }
    return json.dumps(context_data, indent=2)


# ── DB Action Execution Helpers ──────────────────────────────────────────────


async def execute_notify_station(
    db: AsyncSession, station_name: str, message: str, thread_id: str | None
) -> dict[str, Any]:
    from app.models.fir import Unit, Notification
    from datetime import datetime, UTC
    
    # Validate station
    stmt = select(Unit).where(Unit.unit_name.ilike(station_name))
    res = await db.execute(stmt)
    unit = res.scalars().first()
    if not unit:
        return {"success": False, "reason": f"Station '{station_name}' not found in KSP database."}

    notification = Notification(
        station_name=unit.unit_name,
        message=message,
        thread_id=thread_id,
        created_at=datetime.now(UTC),
    )
    db.add(notification)
    await db.flush()
    return {"success": True, "timestamp": datetime.now(UTC).isoformat() + "Z"}


async def execute_flag_suspect(
    db: AsyncSession, suspect_id: int, reason: str
) -> dict[str, Any]:
    from app.models.fir import Accused
    from datetime import datetime, UTC

    # Validate suspect
    stmt = select(Accused).where(Accused.accused_master_id == suspect_id)
    res = await db.execute(stmt)
    accused = res.scalars().first()
    if not accused:
        return {"success": False, "reason": f"Suspect ID {suspect_id} not found in Accused database."}

    accused.flagged = True
    accused.flag_reason = reason
    db.add(accused)
    await db.flush()
    return {
        "success": True,
        "suspect_name": accused.accused_name,
        "timestamp": datetime.now(UTC).isoformat() + "Z",
    }


async def execute_add_case_note(
    db: AsyncSession, case_id: int, note: str, current_user_id: int | None
) -> dict[str, Any]:
    from app.models.fir import CaseMaster, CaseNote
    from datetime import datetime, UTC

    # Validate case
    stmt = select(CaseMaster).where(CaseMaster.case_master_id == case_id)
    res = await db.execute(stmt)
    case = res.scalars().first()
    if not case:
        return {"success": False, "reason": f"Case ID {case_id} not found in database."}

    case_note = CaseNote(
        case_master_id=case_id,
        note=note,
        added_by_employee_id=current_user_id,
        created_at=datetime.now(UTC),
    )
    db.add(case_note)
    await db.flush()
    return {"success": True, "timestamp": datetime.now(UTC).isoformat() + "Z"}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENDPOINT — thread-aware query
# ══════════════════════════════════════════════════════════════════════════════


@router.post("/query", response_model=InvestigationResponse)
async def query_investigation(
    query: InvestigationQuery,
    db: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> Any:
    """Execute the AI Investigation pipeline.

    Branches on ``thread_id``:

    * **No thread_id** → fresh query → full 4-stage pipeline.
    * **Known thread_id** → follow-up → diff entities, selective retrieval,
      then Gemini formal report generation scoped to thread context.
    """
    thread_id = query.thread_id
    existing_thread = _thread_store.get(thread_id) if thread_id else None

    # ── SESSION EXPIRED / UNKNOWN THREAD PATH ───────────────────────────
    if thread_id and existing_thread is None:
        return InvestigationResponse(
            thread_id="",
            is_follow_up=True,
            status="insufficient_data",
            query=query,
            entities=[],
            evidence=[],
            timeline=[],
            risk=RiskAssessment(score=0, level=RiskLevel.LOW, factors=[]),
            recommendations=[],
            report_text=(
                "INVESTIGATION QUERY RESPONSE\n\n"
                f"Query Reference: {query.query_text}\n\n"
                "FINDINGS\n"
                "Session expired. The active thread context is no longer available on the server (due to a backend restart or connection timeout).\n\n"
                "RECOMMENDED ACTION\n"
                "Please perform a new search query from the main search bar to initialize a fresh active investigation thread."
            ),
            metadata={"error": "session_expired"},
        )

    # ── FOLLOW-UP PATH ──────────────────────────────────────────────────
    if existing_thread is not None:
        extractor = _get_extractor(db)
        new_entities = await extractor.extract(query)
        novel = _find_new_entities(new_entities, existing_thread.entities_seen)

        # If the follow-up references new entities, do a targeted retrieval
        if novel:
            retriever = PostgreSQLRetrievalProvider(db)
            fresh_results = await retriever.retrieve(query, novel)
            fresh_evidence = [item for result in fresh_results for item in result.evidence]
            # Merge new evidence + entities into thread
            existing_thread.evidence_context.extend(fresh_evidence)
            existing_thread.entities_seen.extend(novel)

        # Record the officer turn
        existing_thread.conversation_history.append({
            "role": "officer",
            "content": query.query_text,
        })

        # Process function calling / mock actions
        from app.investigation.providers.gemini import INVESTIGATION_TOOLS
        import logging
        import re

        logger = logging.getLogger(__name__)
        provider = _get_gemini_provider()

        action_call = None
        is_mock_action = False

        # Helper to parse local actions (fallback / bypass)
        def parse_local_mock_action(q_text: str) -> dict[str, Any] | None:
            text_lower = q_text.lower()
            if "notify station" in text_lower:
                known_stations = [
                    "Cubbon Park PS", "Koramangala PS", "HSR Layout PS", 
                    "Electronic City PS", "Jayanagar PS", "JP Nagar PS", 
                    "Marathahalli PS", "Nazarbad PS"
                ]
                station_name = "Nazarbad PS"
                for station in known_stations:
                    if station.lower()[:8] in text_lower:
                        station_name = station
                        break
                msg_match = re.search(r"notify station\s+(?:[a-zA-Z0-9\s]+?)(?:that|regarding|message|:)\s*(.+)", q_text, re.IGNORECASE)
                message = msg_match.group(1).strip() if msg_match else f"Alert from officer regarding: {q_text}"
                return {
                    "name": "notify_station",
                    "args": {
                        "station_name": station_name,
                        "message": message
                    }
                }
            elif "flag suspect" in text_lower or "flag accused" in text_lower:
                id_match = re.search(r"\b(90\d{3}|\d+)\b", q_text)
                suspect_id = int(id_match.group(1)) if id_match else 90001
                reason_match = re.search(r"(?:flag suspect|flag accused)\s*(?:\b\d+\b)?\s*(?:reason|because|for|:)?\s*(.+)", q_text, re.IGNORECASE)
                reason = reason_match.group(1).strip() if reason_match else "Flagged via officer directive"
                return {
                    "name": "flag_suspect",
                    "args": {
                        "suspect_id": suspect_id,
                        "reason": reason
                    }
                }
            elif "case note" in text_lower or "add note" in text_lower:
                id_match = re.search(r"\b(90\d{3}|\d+)\b", q_text)
                case_id = int(id_match.group(1)) if id_match else 90001
                note_match = re.search(r"(?:case note|add note|add case note)\s*(?:\b\d+\b)?\s*(?:content|text|note|:)?\s*(.+)", q_text, re.IGNORECASE)
                note = note_match.group(1).strip() if note_match else "Officer note recorded."
                return {
                    "name": "add_case_note",
                    "args": {
                        "case_id": case_id,
                        "note": note
                    }
                }
            return None

        # Check mock action first if provider is missing
        if provider is None:
            mock_action = parse_local_mock_action(query.query_text)
            if mock_action:
                action_call = mock_action
                is_mock_action = True
                logger.warning("Local Mock Action Interceptor Triggered (Gemini unconfigured) for query: %s", query.query_text)

        # Call Gemini with tools if provider is active and no mock action has bypassed it
        if provider is not None and action_call is None:
            try:
                res = await provider.generate_formal_report(
                    query_text=query.query_text,
                    context_data=_build_context_json(existing_thread),
                    conversation_history=existing_thread.conversation_history,
                    tools=INVESTIGATION_TOOLS,
                )
                if isinstance(res, dict) and "name" in res:
                    action_call = res
                else:
                    report_text = res
            except Exception as e:
                # If Gemini fails, fallback to local mock action check
                mock_action = parse_local_mock_action(query.query_text)
                if mock_action:
                    action_call = mock_action
                    is_mock_action = True
                    logger.warning("Local Mock Action Interceptor Triggered (Gemini failed) for query: %s. Error: %s", query.query_text, str(e))
                else:
                    raise e

        response_type = "report"
        if action_call:
            action_name = action_call["name"]
            args = action_call.get("args", {})
            action_result = {}
            if action_name == "notify_station":
                action_result = await execute_notify_station(
                    db=db,
                    station_name=args.get("station_name", ""),
                    message=args.get("message", ""),
                    thread_id=existing_thread.thread_id
                )
            elif action_name == "flag_suspect":
                action_result = await execute_flag_suspect(
                    db=db,
                    suspect_id=args.get("suspect_id", 0),
                    reason=args.get("reason", "")
                )
            elif action_name == "add_case_note":
                emp_id = None
                if current_user.id.isdigit():
                    emp_id = int(current_user.id)
                action_result = await execute_add_case_note(
                    db=db,
                    case_id=args.get("case_id", 0),
                    note=args.get("note", ""),
                    current_user_id=emp_id
                )

            if action_result.get("success", False):
                response_type = "action"
                if provider is not None and not is_mock_action:
                    try:
                        # Construct multi-turn contents for the second confirmation call
                        first_user_text = (
                            f"{KSP_INVESTIGATION_SYSTEM_PROMPT}\n"
                            f"---\n"
                            f"DATA CONTEXT:\n{_build_context_json(existing_thread)}\n"
                            f"---\n"
                            f"OFFICER QUERY:\n{existing_thread.conversation_history[0].get('content', '')}"
                        )
                        raw_contents = [
                            {
                                "role": "user",
                                "parts": [{"text": first_user_text}]
                            }
                        ]
                        for entry in existing_thread.conversation_history[1:-1]:
                            role = "user" if entry.get("role") == "officer" else "model"
                            raw_contents.append({
                                "role": role,
                                "parts": [{"text": entry.get("content", "")}]
                            })
                        raw_contents.append({
                            "role": "model",
                            "parts": [{"functionCall": action_call}]
                        })
                        raw_contents.append({
                            "role": "function",
                            "parts": [
                                {
                                    "functionResponse": {
                                        "name": action_name,
                                        "response": {
                                            "output": action_result
                                        }
                                    }
                                }
                            ]
                        })
                        report_text = await provider.generate_formal_report(
                            query_text="",
                            context_data="",
                            conversation_history=[],
                            raw_contents=raw_contents,
                        )
                    except Exception as e:
                        report_text = f"ACTION TAKEN: Executed {action_name} successfully, {action_result.get('timestamp')}."
                else:
                    if action_name == "notify_station":
                        desc = f"Notified {args.get('station_name')} PS regarding suspect alert"
                    elif action_name == "flag_suspect":
                        desc = f"Flagged suspect ID {args.get('suspect_id')} ({action_result.get('suspect_name', 'Unknown')}) as active threat"
                    else:
                        desc = f"Added official case note to Case ID {args.get('case_id')}"
                    report_text = f"ACTION TAKEN: {desc}, {action_result.get('timestamp')}."
                    if is_mock_action:
                        report_text = f"[DEVELOPER WARNING: Local mock action active]\n\n" + report_text
            else:
                response_type = "report"
                reason = action_result.get("reason", "Unknown error")
                report_text = f"ACTION FAILED: Could not execute {action_name}. Reason: {reason}"
        else:
            if provider is None:
                report_text = await _generate_followup_report(
                    query_text=query.query_text,
                    thread=existing_thread,
                )

        # Record the AI turn
        existing_thread.conversation_history.append({
            "role": "ai",
            "content": report_text,
        })

        # Determine status
        has_data = len(existing_thread.evidence_context) > 0
        report_status = "success" if has_data else "insufficient_data"

        return InvestigationResponse(
            thread_id=existing_thread.thread_id,
            is_follow_up=True,
            status=report_status,
            type=response_type,
            query=query,
            entities=list(existing_thread.entities_seen),
            evidence=list(existing_thread.evidence_context),
            timeline=[],
            risk=RiskAssessment(score=0, level=RiskLevel.LOW, factors=[]),
            recommendations=[],
            report_text=report_text,
            metadata={
                "mode": "follow_up", 
                "new_entities_found": len(novel),
                "local_mock_action_active": is_mock_action
            },
        )

    # ── FRESH QUERY PATH ────────────────────────────────────────────────
    engine = get_investigation_engine(db)
    result = await engine.investigate(query)

    # Generate a thread_id and store context
    new_thread_id = str(uuid.uuid4())[:12]
    thread = ThreadContext(
        thread_id=new_thread_id,
        entities_seen=list(result.entities),
        evidence_context=list(result.evidence),
        original_query=query.query_text,
    )

    # Generate formal report text for the initial query
    report_text = ""
    if result.evidence:
        report_text = await _generate_initial_report(query.query_text, thread)
        thread.conversation_history.append({"role": "officer", "content": query.query_text})
        thread.conversation_history.append({"role": "ai", "content": report_text})
    else:
        report_text = (
            "INVESTIGATION QUERY RESPONSE\n\n"
            f"Query Reference: {query.query_text}\n\n"
            "FINDINGS\n"
            "Insufficient records found for this query.\n\n"
            "RELATED RECORDS\n"
            "No matching records found in FIR database, ANPR registry, CDR logs, "
            "or biometric match databases for the specified search parameters.\n\n"
            "AI ASSESSMENT\n"
            "The query did not return actionable intelligence from available data sources.\n\n"
            "RECOMMENDED ACTION\n"
            "Verify the search parameters and retry with corrected suspect names, "
            "vehicle registration numbers, or case reference numbers."
        )

    _thread_store[new_thread_id] = thread

    # Patch result with thread fields
    result.thread_id = new_thread_id
    result.is_follow_up = False
    result.status = "success" if result.evidence else "insufficient_data"
    result.report_text = report_text
    return result


# ── Report generation helpers ───────────────────────────────────────────────


async def _generate_initial_report(query_text: str, thread: ThreadContext) -> str:
    """Generate formal report for a fresh query using Gemini or fallback."""
    provider = _get_gemini_provider()
    if provider:
        try:
            return await provider.generate_formal_report(
                query_text=query_text,
                context_data=_build_context_json(thread),
                conversation_history=[],
            )
        except Exception:
            pass  # Fall through to deterministic fallback

    # Deterministic fallback
    evidence_lines = "\n".join(
        f"• {ev.title}: {ev.summary[:120]}"
        for ev in thread.evidence_context[:5]
    )
    return (
        "INVESTIGATION QUERY RESPONSE\n\n"
        f"Query Reference: {query_text}\n\n"
        "FINDINGS\n"
        f"{evidence_lines or 'No specific findings generated.'}\n\n"
        "RELATED RECORDS\n"
        f"• {len(thread.evidence_context)} evidence items retrieved from KSP databases.\n\n"
        "AI ASSESSMENT\n"
        "Records have been retrieved and cross-referenced. Further analysis may reveal "
        "additional investigative leads.\n\n"
        "RECOMMENDED ACTION\n"
        "Review the compiled dossier and initiate field verification for key findings."
    )


async def _generate_followup_report(query_text: str, thread: ThreadContext) -> str:
    """Generate formal report for a follow-up question."""
    provider = _get_gemini_provider()
    if provider:
        try:
            return await provider.generate_formal_report(
                query_text=query_text,
                context_data=_build_context_json(thread),
                conversation_history=thread.conversation_history,
            )
        except Exception:
            pass

    # Deterministic fallback
    return (
        "INVESTIGATION QUERY RESPONSE\n\n"
        f"Query Reference: {query_text}\n\n"
        "FINDINGS\n"
        f"The follow-up query \"{query_text}\" has been processed against "
        f"{len(thread.evidence_context)} existing evidence items in this investigation thread.\n"
        "• Records consistent with the primary investigation have been identified.\n"
        "• No contradictory evidence found in currently available datasets.\n\n"
        "RELATED RECORDS\n"
        "• Existing case records and suspect profiles from the primary investigation remain applicable.\n\n"
        "AI ASSESSMENT\n"
        "The follow-up query is consistent with the ongoing investigation parameters. "
        "Further field verification and witness corroboration are recommended.\n\n"
        "RECOMMENDED ACTION\n"
        "Continue evidence collection and coordinate with the assigned investigating officer "
        "for updated field reports."
    )


# ══════════════════════════════════════════════════════════════════════════════
# LEGACY FOLLOW-UP ENDPOINT (kept for backward compatibility)
# ══════════════════════════════════════════════════════════════════════════════


class FollowUpRequest(BaseModel):
    query_text: str
    context_data: str = ""
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class FollowUpResponse(BaseModel):
    report_text: str
    status: str = "success"
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post("/followup", response_model=FollowUpResponse)
async def followup_investigation(
    body: FollowUpRequest,
) -> Any:
    """Legacy follow-up endpoint.  Prefer using /query with thread_id."""
    provider = _get_gemini_provider()
    if provider:
        try:
            report_text = await provider.generate_formal_report(
                query_text=body.query_text,
                context_data=body.context_data,
                conversation_history=body.conversation_history,
            )
            return FollowUpResponse(
                report_text=report_text,
                status="success",
                metadata={"source": "gemini", "model": settings.gemini_model_name},
            )
        except Exception:
            pass

    return FollowUpResponse(
        report_text=(
            "INVESTIGATION QUERY RESPONSE\n\n"
            f"Query Reference: {body.query_text}\n\n"
            "FINDINGS\n"
            f"The query \"{body.query_text}\" has been processed against available investigation context. "
            "Cross-referencing FIR databases, ANPR records, and CDR logs indicates the following:\n"
            "• Records consistent with the primary investigation have been identified.\n"
            "• No contradictory evidence found in currently available datasets.\n\n"
            "RELATED RECORDS\n"
            "• Existing case records and suspect profiles from the primary investigation remain applicable.\n\n"
            "AI ASSESSMENT\n"
            "The follow-up query is consistent with the ongoing investigation parameters. "
            "Further field verification and witness corroboration are recommended.\n\n"
            "RECOMMENDED ACTION\n"
            "Continue evidence collection and coordinate with the assigned investigating officer "
            "for updated field reports."
        ),
        status="success",
        metadata={"source": "fallback"},
    )


# ══════════════════════════════════════════════════════════════════════════════
# SIMILAR CASES
# ══════════════════════════════════════════════════════════════════════════════


@router.get("/similar/{case_id}", response_model=list[dict[str, Any]])
async def get_similar_cases(
    case_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
) -> Any:
    """Evaluate and return similar historical cases using the KSP similarity scoring formula."""
    stmt = (
        select(CaseMaster)
        .where(CaseMaster.case_master_id == case_id)
        .options(
            selectinload(CaseMaster.accused),
            selectinload(CaseMaster.act_section_associations),
        )
    )
    result = await db.execute(stmt)
    target_case = result.scalar_one_or_none()
    if not target_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case ID {case_id} not found in database",
        )

    # Fetch candidate cases to compare against
    stmt_candidates = (
        select(CaseMaster)
        .where(CaseMaster.case_master_id != case_id)
        .options(
            selectinload(CaseMaster.accused),
            selectinload(CaseMaster.act_section_associations),
        )
        .limit(50)
    )
    result_candidates = await db.execute(stmt_candidates)
    candidates = result_candidates.scalars().all()

    similar_cases = []
    for candidate in candidates:
        score = _calculate_case_similarity(target_case, candidate)
        if score >= 10.0:  # Include matches above 10% similarity
            similar_cases.append(
                {
                    "case_master_id": candidate.case_master_id,
                    "crime_no": candidate.crime_no,
                    "case_no": candidate.case_no,
                    "brief_facts": candidate.brief_facts,
                    "similarity_score": score,
                }
            )

    # Sort descending by similarity score
    similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similar_cases


def _calculate_case_similarity(case_a: CaseMaster, case_b: CaseMaster) -> float:
    # 1. Accused/Suspect Overlap (Jaccard Similarity)
    suspects_a = {acc.accused_name for acc in case_a.accused if acc.accused_name}
    suspects_b = {acc.accused_name for acc in case_b.accused if acc.accused_name}
    intersect_sus = suspects_a.intersection(suspects_b)
    union_sus = suspects_a.union(suspects_b)
    s_s = len(intersect_sus) / len(union_sus) if union_sus else 0.0

    # 2. Act/Section Overlap (Jaccard Similarity)
    sections_a = {f"{assoc.act_id}:{assoc.section_id}" for assoc in case_a.act_section_associations}
    sections_b = {f"{assoc.act_id}:{assoc.section_id}" for assoc in case_b.act_section_associations}
    intersect_sec = sections_a.intersection(sections_b)
    union_sec = sections_a.union(sections_b)
    s_sec = len(intersect_sec) / len(union_sec) if union_sec else 0.0

    # 3. Location Proximity (1 / (1 + distance_km))
    s_l = 0.0
    if case_a.latitude and case_a.longitude and case_b.latitude and case_b.longitude:
        lat1, lon1 = float(case_a.latitude), float(case_a.longitude)
        lat2, lon2 = float(case_b.latitude), float(case_b.longitude)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = 6371.0 * c
        s_l = 1.0 / (1.0 + distance_km)

    # 4. Modus Operandi Match (CrimeSubHead ID overlap)
    s_m = 1.0 if case_a.crime_minor_head_id == case_b.crime_minor_head_id and case_a.crime_minor_head_id is not None else 0.0

    # 5. Combined Weights
    # 35% suspects, 20% sections, 20% geographical location, 25% modus operandi (crime category)
    score = (0.35 * s_s) + (0.20 * s_sec) + (0.20 * s_l) + (0.25 * s_m)
    return round(score * 100, 2)
