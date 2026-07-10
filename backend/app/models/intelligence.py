"""Intelligence and investigation support models.

These extend the official KSP schema with modern intelligence data
structures for AI-powered investigation features.  They integrate
with the existing CaseMaster / Accused / Employee models via FKs.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UnicodeText,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


# ── Vehicles ────────────────────────────────────────────────────────────────

class IntelVehicle(Base):
    __tablename__ = "intel_vehicle"

    vehicle_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    registration_no: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    vehicle_type: Mapped[str | None] = mapped_column(String(50))
    make: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    color: Mapped[str | None] = mapped_column(String(30))
    year: Mapped[int | None] = mapped_column(Integer)
    chassis_no: Mapped[str | None] = mapped_column(String(50))
    engine_no: Mapped[str | None] = mapped_column(String(50))
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    flag_reason: Mapped[str | None] = mapped_column(Text)

    ownerships: Mapped[list[VehicleOwnership]] = relationship(back_populates="vehicle")
    anpr_hits: Mapped[list[ANPRHit]] = relationship(back_populates="vehicle")


class VehicleOwnership(Base):
    __tablename__ = "intel_vehicle_ownership"
    __table_args__ = (Index("ix_vown_vehicle_owner", "vehicle_id", "owner_accused_id"),)

    ownership_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("intel_vehicle.vehicle_id"), index=True)
    owner_name: Mapped[str | None] = mapped_column(String(200))
    owner_accused_id: Mapped[int | None] = mapped_column(
        ForeignKey("Accused.AccusedMasterID"), index=True
    )
    ownership_from: Mapped[date | None] = mapped_column(Date)
    ownership_to: Mapped[date | None] = mapped_column(Date)

    vehicle: Mapped[IntelVehicle] = relationship(back_populates="ownerships")


class VehicleMovement(Base):
    __tablename__ = "intel_vehicle_movement"

    movement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("intel_vehicle.vehicle_id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric)
    location_description: Mapped[str | None] = mapped_column(String(300))
    source: Mapped[str | None] = mapped_column(String(50))  # ANPR / CCTV / manual


# ── ANPR ────────────────────────────────────────────────────────────────────

class ANPRHit(Base):
    __tablename__ = "intel_anpr_hit"
    __table_args__ = (Index("ix_anpr_ts", "captured_at"),)

    anpr_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("intel_vehicle.vehicle_id"), index=True)
    camera_id: Mapped[str | None] = mapped_column(String(50), index=True)
    camera_location: Mapped[str | None] = mapped_column(String(300))
    captured_at: Mapped[datetime] = mapped_column(DateTime)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric)
    confidence: Mapped[float | None] = mapped_column(Float)
    plate_image_url: Mapped[str | None] = mapped_column(String(500))
    direction: Mapped[str | None] = mapped_column(String(20))

    vehicle: Mapped[IntelVehicle] = relationship(back_populates="anpr_hits")


# ── CCTV ────────────────────────────────────────────────────────────────────

class CCTVEvent(Base):
    __tablename__ = "intel_cctv_event"
    __table_args__ = (Index("ix_cctv_ts", "event_time"),)

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str | None] = mapped_column(String(50), index=True)
    camera_location: Mapped[str | None] = mapped_column(String(300))
    event_time: Mapped[datetime] = mapped_column(DateTime)
    event_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    case_master_id: Mapped[int | None] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    latitude: Mapped[Decimal | None] = mapped_column(Numeric)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric)
    footage_url: Mapped[str | None] = mapped_column(String(500))
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)


# ── Evidence ────────────────────────────────────────────────────────────────

class Evidence(Base):
    __tablename__ = "intel_evidence"

    evidence_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    evidence_type: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(UnicodeText)
    collected_date: Mapped[date | None] = mapped_column(Date)
    collected_by_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("Employee.EmployeeID"), index=True
    )
    location: Mapped[str | None] = mapped_column(String(300))
    chain_of_custody: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(30))

    attachments: Mapped[list[EvidenceAttachment]] = relationship(back_populates="evidence")


class EvidenceAttachment(Base):
    __tablename__ = "intel_evidence_attachment"

    attachment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[int] = mapped_column(
        ForeignKey("intel_evidence.evidence_id"), index=True
    )
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_type: Mapped[str | None] = mapped_column(String(30))
    file_size_bytes: Mapped[int | None] = mapped_column(Integer)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime)

    evidence: Mapped[Evidence] = relationship(back_populates="attachments")


# ── Call Detail Records ─────────────────────────────────────────────────────

class PhoneNumber(Base):
    __tablename__ = "intel_phone_number"

    phone_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    owner_name: Mapped[str | None] = mapped_column(String(200))
    accused_master_id: Mapped[int | None] = mapped_column(
        ForeignKey("Accused.AccusedMasterID"), index=True
    )
    imei: Mapped[str | None] = mapped_column(String(20))
    service_provider: Mapped[str | None] = mapped_column(String(50))
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)


class CallDetailRecord(Base):
    __tablename__ = "intel_cdr"
    __table_args__ = (Index("ix_cdr_ts", "call_time"),)

    cdr_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caller_phone_id: Mapped[int] = mapped_column(
        ForeignKey("intel_phone_number.phone_id"), index=True
    )
    receiver_phone_id: Mapped[int] = mapped_column(
        ForeignKey("intel_phone_number.phone_id"), index=True
    )
    call_time: Mapped[datetime] = mapped_column(DateTime)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    call_type: Mapped[str | None] = mapped_column(String(20))  # voice / sms / data
    tower_id: Mapped[str | None] = mapped_column(String(50))
    tower_location: Mapped[str | None] = mapped_column(String(300))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric)
    case_master_id: Mapped[int | None] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )


# ── Timeline ───────────────────────────────────────────────────────────────

class TimelineEvent(Base):
    __tablename__ = "intel_timeline_event"
    __table_args__ = (Index("ix_timeline_case_ts", "case_master_id", "event_time"),)

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    event_time: Mapped[datetime] = mapped_column(DateTime)
    event_type: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(UnicodeText)
    source: Mapped[str | None] = mapped_column(String(50))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric)
    actor_name: Mapped[str | None] = mapped_column(String(200))
    severity: Mapped[str | None] = mapped_column(String(20))  # low / medium / high / critical


# ── Investigation support ──────────────────────────────────────────────────

class InvestigationSession(Base):
    __tablename__ = "intel_investigation_session"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    started_by_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("Employee.EmployeeID"), index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)
    session_type: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(30))
    summary: Mapped[str | None] = mapped_column(UnicodeText)


class CriminalRelationship(Base):
    __tablename__ = "intel_criminal_relationship"
    __table_args__ = (
        Index("ix_crimrel_pair", "accused_id_1", "accused_id_2"),
    )

    relationship_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    accused_id_1: Mapped[int] = mapped_column(
        ForeignKey("Accused.AccusedMasterID"), index=True
    )
    accused_id_2: Mapped[int] = mapped_column(
        ForeignKey("Accused.AccusedMasterID"), index=True
    )
    relationship_type: Mapped[str | None] = mapped_column(String(50))
    strength: Mapped[float | None] = mapped_column(Float)
    detected_via: Mapped[str | None] = mapped_column(String(50))
    case_master_id: Mapped[int | None] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )


class InvestigationNote(Base):
    __tablename__ = "intel_investigation_note"

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    author_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("Employee.EmployeeID"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[str | None] = mapped_column(UnicodeText)
    note_type: Mapped[str | None] = mapped_column(String(50))
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)


class AIReport(Base):
    __tablename__ = "intel_ai_report"

    report_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    report_type: Mapped[str | None] = mapped_column(String(50))
    generated_at: Mapped[datetime] = mapped_column(DateTime)
    content: Mapped[str | None] = mapped_column(UnicodeText)
    model_name: Mapped[str | None] = mapped_column(String(50))
    confidence: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str | None] = mapped_column(String(30))


class RiskAssessment(Base):
    __tablename__ = "intel_risk_assessment"

    assessment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column(
        ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    assessed_at: Mapped[datetime] = mapped_column(DateTime)
    risk_level: Mapped[str | None] = mapped_column(String(20))
    risk_score: Mapped[float | None] = mapped_column(Float)
    factors: Mapped[str | None] = mapped_column(UnicodeText)
    recommendations: Mapped[str | None] = mapped_column(UnicodeText)
    assessed_by: Mapped[str | None] = mapped_column(String(50))  # ai / human
