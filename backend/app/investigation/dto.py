from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class EntityType(StrEnum):
    PERSON = "person"
    VEHICLE = "vehicle"
    CASE = "case"
    LOCATION = "location"
    PHONE = "phone"
    ORGANIZATION = "organization"
    DATE = "date"
    UNKNOWN = "unknown"


class EvidenceType(StrEnum):
    FIR = "fir"
    SUSPECT = "suspect"
    VEHICLE = "vehicle"
    REPORT = "report"
    CCTV = "cctv"
    CALL_LOG = "call_log"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ConversationTurn(BaseModel):
    role: str  # "officer" or "ai"
    content: str


class InvestigationQuery(BaseModel):
    query_text: str = Field(min_length=1)
    requested_by: str
    thread_id: str | None = None
    is_follow_up: bool = False
    conversation_history: list[ConversationTurn] = Field(default_factory=list)
    jurisdiction_id: str | None = None
    filters: dict[str, Any] = Field(default_factory=dict)


class ExtractedEntity(BaseModel):
    value: str
    entity_type: EntityType
    confidence: float = Field(ge=0, le=1)
    source: str = "engine"
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    source_name: str
    evidence: list["EvidenceCandidate"] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceCandidate(BaseModel):
    id: str
    evidence_type: EvidenceType
    title: str
    summary: str
    occurred_at: datetime | None = None
    source: str
    confidence: float = Field(default=0, ge=0, le=1)
    relevance_score: float = Field(default=0, ge=0, le=1)
    risk_weight: float = Field(default=0, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TimelineEvent(BaseModel):
    title: str
    occurred_at: datetime
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class RiskAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    factors: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    title: str
    description: str
    priority: RecommendationPriority
    rationale: str
    related_evidence_ids: list[str] = Field(default_factory=list)


class InvestigationResponse(BaseModel):
    thread_id: str = ""
    is_follow_up: bool = False
    status: Literal["success", "insufficient_data"] = "success"
    type: Literal["report", "action"] = "report"
    query: InvestigationQuery
    entities: list[ExtractedEntity] = Field(default_factory=list)
    evidence: list[EvidenceCandidate] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    risk: RiskAssessment
    recommendations: list[Recommendation] = Field(default_factory=list)
    report_text: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
