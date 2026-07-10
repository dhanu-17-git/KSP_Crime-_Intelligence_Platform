from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UnicodeText,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class State(Base):
    __tablename__ = "State"

    state_id: Mapped[int] = mapped_column(
        "StateID", Integer, primary_key=True, autoincrement=False
    )
    state_name: Mapped[str | None] = mapped_column("StateName", String)
    nationality_id: Mapped[int | None] = mapped_column("NationalityID", Integer)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    districts: Mapped[list[District]] = relationship(back_populates="state")
    courts: Mapped[list[Court]] = relationship(back_populates="state")
    units: Mapped[list[Unit]] = relationship(back_populates="state")
    arrest_surrenders: Mapped[list[ArrestSurrender]] = relationship(back_populates="state")


class District(Base):
    __tablename__ = "District"

    district_id: Mapped[int] = mapped_column(
        "DistrictID", Integer, primary_key=True, autoincrement=False
    )
    district_name: Mapped[str | None] = mapped_column("DistrictName", String)
    state_id: Mapped[int | None] = mapped_column(
        "StateID", ForeignKey("State.StateID"), index=True
    )
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    state: Mapped[State | None] = relationship(back_populates="districts")
    courts: Mapped[list[Court]] = relationship(back_populates="district")
    units: Mapped[list[Unit]] = relationship(back_populates="district")
    employees: Mapped[list[Employee]] = relationship(back_populates="district")
    arrest_surrenders: Mapped[list[ArrestSurrender]] = relationship(
        back_populates="district"
    )


class Court(Base):
    __tablename__ = "Court"
    __table_args__ = (Index("ix_Court_StateID_DistrictID", "StateID", "DistrictID"),)

    court_id: Mapped[int] = mapped_column(
        "CourtID", Integer, primary_key=True, autoincrement=False
    )
    court_name: Mapped[str | None] = mapped_column("CourtName", String)
    district_id: Mapped[int | None] = mapped_column(
        "DistrictID", ForeignKey("District.DistrictID"), index=True
    )
    state_id: Mapped[int | None] = mapped_column(
        "StateID", ForeignKey("State.StateID"), index=True
    )
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    district: Mapped[District | None] = relationship(back_populates="courts")
    state: Mapped[State | None] = relationship(back_populates="courts")
    cases: Mapped[list[CaseMaster]] = relationship(back_populates="court")
    arrest_surrenders: Mapped[list[ArrestSurrender]] = relationship(
        back_populates="court"
    )


class UnitType(Base):
    __tablename__ = "UnitType"

    unit_type_id: Mapped[int] = mapped_column(
        "UnitTypeID", Integer, primary_key=True, autoincrement=False
    )
    unit_type_name: Mapped[str | None] = mapped_column("UnitTypeName", String)
    city_dist_state: Mapped[str | None] = mapped_column("CityDistState", String)
    hierarchy: Mapped[int | None] = mapped_column("Hierarchy", Integer)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    units: Mapped[list[Unit]] = relationship(back_populates="unit_type")


class Unit(Base):
    __tablename__ = "Unit"
    __table_args__ = (Index("ix_Unit_StateID_DistrictID", "StateID", "DistrictID"),)

    unit_id: Mapped[int] = mapped_column(
        "UnitID", Integer, primary_key=True, autoincrement=False
    )
    unit_name: Mapped[str | None] = mapped_column("UnitName", String)
    type_id: Mapped[int | None] = mapped_column(
        "TypeID", ForeignKey("UnitType.UnitTypeID"), index=True
    )
    parent_unit_id: Mapped[int | None] = mapped_column(
        "ParentUnit", ForeignKey("Unit.UnitID"), index=True
    )
    nationality_id: Mapped[int | None] = mapped_column("NationalityID", Integer)
    state_id: Mapped[int | None] = mapped_column(
        "StateID", ForeignKey("State.StateID"), index=True
    )
    district_id: Mapped[int | None] = mapped_column(
        "DistrictID", ForeignKey("District.DistrictID"), index=True
    )
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    unit_type: Mapped[UnitType | None] = relationship(back_populates="units")
    parent: Mapped[Unit | None] = relationship(
        back_populates="children", remote_side=[unit_id]
    )
    children: Mapped[list[Unit]] = relationship(back_populates="parent")
    state: Mapped[State | None] = relationship(back_populates="units")
    district: Mapped[District | None] = relationship(back_populates="units")
    employees: Mapped[list[Employee]] = relationship(back_populates="unit")
    registered_cases: Mapped[list[CaseMaster]] = relationship(back_populates="police_station")
    arrest_surrenders: Mapped[list[ArrestSurrender]] = relationship(
        back_populates="police_station"
    )


class Rank(Base):
    __tablename__ = "Rank"

    rank_id: Mapped[int] = mapped_column(
        "RankID", Integer, primary_key=True, autoincrement=False
    )
    rank_name: Mapped[str | None] = mapped_column("RankName", String)
    hierarchy: Mapped[int | None] = mapped_column("Hierarchy", Integer)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    employees: Mapped[list[Employee]] = relationship(back_populates="rank")


class Designation(Base):
    __tablename__ = "Designation"

    designation_id: Mapped[int] = mapped_column(
        "DesignationID", Integer, primary_key=True, autoincrement=False
    )
    designation_name: Mapped[str | None] = mapped_column("DesignationName", String)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)
    sort_order: Mapped[int | None] = mapped_column("SortOrder", Integer)

    employees: Mapped[list[Employee]] = relationship(back_populates="designation")


class Employee(Base):
    __tablename__ = "Employee"

    employee_id: Mapped[int] = mapped_column(
        "EmployeeID", Integer, primary_key=True, autoincrement=False
    )
    district_id: Mapped[int | None] = mapped_column(
        "DistrictID", ForeignKey("District.DistrictID"), index=True
    )
    unit_id: Mapped[int | None] = mapped_column(
        "UnitID", ForeignKey("Unit.UnitID"), index=True
    )
    rank_id: Mapped[int | None] = mapped_column(
        "RankID", ForeignKey("Rank.RankID"), index=True
    )
    designation_id: Mapped[int | None] = mapped_column(
        "DesignationID", ForeignKey("Designation.DesignationID"), index=True
    )
    kgid: Mapped[str | None] = mapped_column("KGID", String, unique=True)
    first_name: Mapped[str | None] = mapped_column("FirstName", String)
    employee_dob: Mapped[date | None] = mapped_column("EmployeeDOB", Date)
    gender_id: Mapped[int | None] = mapped_column("GenderID", Integer)
    blood_group_id: Mapped[int | None] = mapped_column("BloodGroupID", Integer)
    physically_challenged: Mapped[bool | None] = mapped_column(
        "PhysicallyChallenged", Boolean
    )
    appointment_date: Mapped[date | None] = mapped_column("AppointmentDate", Date)

    district: Mapped[District | None] = relationship(back_populates="employees")
    unit: Mapped[Unit | None] = relationship(back_populates="employees")
    rank: Mapped[Rank | None] = relationship(back_populates="employees")
    designation: Mapped[Designation | None] = relationship(back_populates="employees")
    registered_cases: Mapped[list[CaseMaster]] = relationship(
        back_populates="registered_by",
        foreign_keys="CaseMaster.police_person_id",
    )
    arrest_surrenders_as_io: Mapped[list[ArrestSurrender]] = relationship(
        back_populates="io",
        foreign_keys="ArrestSurrender.io_id",
    )
    chargesheets: Mapped[list[ChargesheetDetails]] = relationship(
        back_populates="police_person"
    )


class CaseCategory(Base):
    __tablename__ = "CaseCategory"

    case_category_id: Mapped[int] = mapped_column(
        "CaseCategoryID", Integer, primary_key=True, autoincrement=False
    )
    lookup_value: Mapped[str | None] = mapped_column("LookupValue", String)

    cases: Mapped[list[CaseMaster]] = relationship(back_populates="case_category")


class GravityOffence(Base):
    __tablename__ = "GravityOffence"

    gravity_offence_id: Mapped[int] = mapped_column(
        "GravityOffenceID", Integer, primary_key=True, autoincrement=False
    )
    lookup_value: Mapped[str | None] = mapped_column("LookupValue", String)

    cases: Mapped[list[CaseMaster]] = relationship(back_populates="gravity_offence")


class CrimeHead(Base):
    __tablename__ = "CrimeHead"

    crime_head_id: Mapped[int] = mapped_column(
        "CrimeHeadID", Integer, primary_key=True, autoincrement=False
    )
    crime_group_name: Mapped[str | None] = mapped_column("CrimeGroupName", String)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    cases_as_major_head: Mapped[list[CaseMaster]] = relationship(
        back_populates="crime_major_head"
    )
    sub_heads: Mapped[list[CrimeSubHead]] = relationship(back_populates="crime_head")
    act_sections: Mapped[list[CrimeHeadActSection]] = relationship(
        back_populates="crime_head"
    )


class CrimeSubHead(Base):
    __tablename__ = "CrimeSubHead"

    crime_sub_head_id: Mapped[int] = mapped_column(
        "CrimeSubHeadID", Integer, primary_key=True, autoincrement=False
    )
    crime_head_id: Mapped[int | None] = mapped_column(
        "CrimeHeadID", ForeignKey("CrimeHead.CrimeHeadID"), index=True
    )
    crime_head_name: Mapped[str | None] = mapped_column("CrimeHeadName", String)
    seq_id: Mapped[int | None] = mapped_column("SeqID", Integer)

    crime_head: Mapped[CrimeHead | None] = relationship(back_populates="sub_heads")
    cases_as_minor_head: Mapped[list[CaseMaster]] = relationship(
        back_populates="crime_minor_head"
    )


class CaseStatusMaster(Base):
    __tablename__ = "CaseStatusMaster"

    case_status_id: Mapped[int] = mapped_column(
        "CaseStatusID", Integer, primary_key=True, autoincrement=False
    )
    case_status_name: Mapped[str | None] = mapped_column("CaseStatusName", String)

    cases: Mapped[list[CaseMaster]] = relationship(back_populates="case_status")


class CasteMaster(Base):
    __tablename__ = "CasteMaster"

    caste_master_id: Mapped[int] = mapped_column(
        "caste_master_id", Integer, primary_key=True, autoincrement=False
    )
    caste_master_name: Mapped[str | None] = mapped_column("caste_master_name", String)

    complainants: Mapped[list[ComplainantDetails]] = relationship(back_populates="caste")


class ReligionMaster(Base):
    __tablename__ = "ReligionMaster"

    religion_id: Mapped[int] = mapped_column(
        "ReligionID", Integer, primary_key=True, autoincrement=False
    )
    religion_name: Mapped[str | None] = mapped_column("ReligionName", String)

    complainants: Mapped[list[ComplainantDetails]] = relationship(back_populates="religion")


class OccupationMaster(Base):
    __tablename__ = "OccupationMaster"

    occupation_id: Mapped[int] = mapped_column(
        "OccupationID", Integer, primary_key=True, autoincrement=False
    )
    occupation_name: Mapped[str | None] = mapped_column("OccupationName", String)

    complainants: Mapped[list[ComplainantDetails]] = relationship(
        back_populates="occupation"
    )


class Act(Base):
    __tablename__ = "Act"

    act_code: Mapped[str] = mapped_column("ActCode", String, primary_key=True)
    act_description: Mapped[str | None] = mapped_column("ActDescription", String)
    short_name: Mapped[str | None] = mapped_column("ShortName", String)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    sections: Mapped[list[Section]] = relationship(back_populates="act")
    case_associations: Mapped[list[ActSectionAssociation]] = relationship(
        back_populates="act"
    )
    crime_head_associations: Mapped[list[CrimeHeadActSection]] = relationship(
        back_populates="act"
    )


class Section(Base):
    __tablename__ = "Section"

    section_code: Mapped[str] = mapped_column("SectionCode", String, primary_key=True)
    act_code: Mapped[str | None] = mapped_column(
        "ActCode", ForeignKey("Act.ActCode"), index=True
    )
    section_description: Mapped[str | None] = mapped_column("SectionDescription", String)
    active: Mapped[bool | None] = mapped_column("Active", Boolean)

    act: Mapped[Act | None] = relationship(back_populates="sections")
    case_associations: Mapped[list[ActSectionAssociation]] = relationship(
        back_populates="section"
    )
    crime_head_associations: Mapped[list[CrimeHeadActSection]] = relationship(
        back_populates="section"
    )


class CaseMaster(Base):
    __tablename__ = "CaseMaster"
    __table_args__ = (
        UniqueConstraint("CrimeNo", name="uq_CaseMaster_CrimeNo"),
        UniqueConstraint(
            "PoliceStationID",
            "CaseCategoryID",
            "CaseNo",
            name="uq_CaseMaster_station_category_case_no",
        ),
        Index("ix_CaseMaster_registered_station", "PoliceStationID", "CrimeRegisteredDate"),
        Index("ix_CaseMaster_crime_heads", "CrimeMajorHeadID", "CrimeMinorHeadID"),
    )

    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", Integer, primary_key=True, autoincrement=False
    )
    crime_no: Mapped[str | None] = mapped_column("CrimeNo", String)
    case_no: Mapped[str | None] = mapped_column("CaseNo", String)
    crime_registered_date: Mapped[date | None] = mapped_column("CrimeRegisteredDate", Date)
    police_person_id: Mapped[int | None] = mapped_column(
        "PolicePersonID", ForeignKey("Employee.EmployeeID"), index=True
    )
    police_station_id: Mapped[int | None] = mapped_column(
        "PoliceStationID", ForeignKey("Unit.UnitID"), index=True
    )
    case_category_id: Mapped[int | None] = mapped_column(
        "CaseCategoryID", ForeignKey("CaseCategory.CaseCategoryID"), index=True
    )
    gravity_offence_id: Mapped[int | None] = mapped_column(
        "GravityOffenceID", ForeignKey("GravityOffence.GravityOffenceID"), index=True
    )
    crime_major_head_id: Mapped[int | None] = mapped_column(
        "CrimeMajorHeadID", ForeignKey("CrimeHead.CrimeHeadID"), index=True
    )
    crime_minor_head_id: Mapped[int | None] = mapped_column(
        "CrimeMinorHeadID", ForeignKey("CrimeSubHead.CrimeSubHeadID"), index=True
    )
    case_status_id: Mapped[int | None] = mapped_column(
        "CaseStatusID", ForeignKey("CaseStatusMaster.CaseStatusID"), index=True
    )
    court_id: Mapped[int | None] = mapped_column(
        "CourtID", ForeignKey("Court.CourtID"), index=True
    )
    incident_from_date: Mapped[datetime | None] = mapped_column("IncidentFromDate", DateTime)
    incident_to_date: Mapped[datetime | None] = mapped_column("IncidentToDate", DateTime)
    info_received_ps_date: Mapped[datetime | None] = mapped_column(
        "InfoReceivedPSDate", DateTime
    )
    latitude: Mapped[Decimal | None] = mapped_column("latitude", Numeric)
    longitude: Mapped[Decimal | None] = mapped_column("longitude", Numeric)
    brief_facts: Mapped[str | None] = mapped_column("BriefFacts", UnicodeText)

    registered_by: Mapped[Employee | None] = relationship(
        back_populates="registered_cases",
        foreign_keys=[police_person_id],
    )
    police_station: Mapped[Unit | None] = relationship(
        back_populates="registered_cases",
        foreign_keys=[police_station_id],
    )
    case_category: Mapped[CaseCategory | None] = relationship(back_populates="cases")
    gravity_offence: Mapped[GravityOffence | None] = relationship(back_populates="cases")
    crime_major_head: Mapped[CrimeHead | None] = relationship(
        back_populates="cases_as_major_head"
    )
    crime_minor_head: Mapped[CrimeSubHead | None] = relationship(
        back_populates="cases_as_minor_head"
    )
    case_status: Mapped[CaseStatusMaster | None] = relationship(back_populates="cases")
    court: Mapped[Court | None] = relationship(back_populates="cases")
    complainants: Mapped[list[ComplainantDetails]] = relationship(back_populates="case")
    victims: Mapped[list[Victim]] = relationship(back_populates="case")
    accused: Mapped[list[Accused]] = relationship(back_populates="case")
    arrest_surrenders: Mapped[list[ArrestSurrender]] = relationship(back_populates="case")
    act_section_associations: Mapped[list[ActSectionAssociation]] = relationship(
        back_populates="case"
    )
    occurrence_time: Mapped[InvOccuranceTime | None] = relationship(
        back_populates="case", uselist=False
    )
    chargesheets: Mapped[list[ChargesheetDetails]] = relationship(back_populates="case")


class InvOccuranceTime(Base):
    __tablename__ = "Inv_OccuranceTime"

    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), primary_key=True
    )

    case: Mapped[CaseMaster] = relationship(back_populates="occurrence_time")


class ComplainantDetails(Base):
    __tablename__ = "ComplainantDetails"

    complainant_id: Mapped[int] = mapped_column(
        "ComplainantID", Integer, primary_key=True, autoincrement=False
    )
    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    complainant_name: Mapped[str | None] = mapped_column("ComplainantName", String)
    age_year: Mapped[int | None] = mapped_column("AgeYear", Integer)
    occupation_id: Mapped[int | None] = mapped_column(
        "OccupationID", ForeignKey("OccupationMaster.OccupationID"), index=True
    )
    religion_id: Mapped[int | None] = mapped_column(
        "ReligionID", ForeignKey("ReligionMaster.ReligionID"), index=True
    )
    caste_id: Mapped[int | None] = mapped_column(
        "CasteID", ForeignKey("CasteMaster.caste_master_id"), index=True
    )
    gender_id: Mapped[int | None] = mapped_column("GenderID", Integer)

    case: Mapped[CaseMaster] = relationship(back_populates="complainants")
    occupation: Mapped[OccupationMaster | None] = relationship(back_populates="complainants")
    religion: Mapped[ReligionMaster | None] = relationship(back_populates="complainants")
    caste: Mapped[CasteMaster | None] = relationship(back_populates="complainants")


class ActSectionAssociation(Base):
    __tablename__ = "ActSectionAssociation"
    __table_args__ = (
        Index("ix_ActSectionAssociation_ActID_SectionID", "ActID", "SectionID"),
    )

    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID",
        ForeignKey("CaseMaster.CaseMasterID"),
        primary_key=True,
    )
    act_id: Mapped[str] = mapped_column(
        "ActID", ForeignKey("Act.ActCode"), primary_key=True
    )
    section_id: Mapped[str] = mapped_column(
        "SectionID", ForeignKey("Section.SectionCode"), primary_key=True
    )
    act_order_id: Mapped[int | None] = mapped_column("ActOrderID", Integer)
    section_order_id: Mapped[int | None] = mapped_column("SectionOrderID", Integer)

    case: Mapped[CaseMaster] = relationship(back_populates="act_section_associations")
    act: Mapped[Act] = relationship(back_populates="case_associations")
    section: Mapped[Section] = relationship(back_populates="case_associations")


class Victim(Base):
    __tablename__ = "Victim"

    victim_master_id: Mapped[int] = mapped_column(
        "VictimMasterID", Integer, primary_key=True, autoincrement=False
    )
    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    victim_name: Mapped[str | None] = mapped_column("VictimName", String)
    age_year: Mapped[int | None] = mapped_column("AgeYear", Integer)
    gender_id: Mapped[int | None] = mapped_column("GenderID", Integer)
    victim_police: Mapped[str | None] = mapped_column("VictimPolice", String)

    case: Mapped[CaseMaster] = relationship(back_populates="victims")


class Accused(Base):
    __tablename__ = "Accused"

    accused_master_id: Mapped[int] = mapped_column(
        "AccusedMasterID", Integer, primary_key=True, autoincrement=False
    )
    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    accused_name: Mapped[str | None] = mapped_column("AccusedName", String)
    age_year: Mapped[int | None] = mapped_column("AgeYear", Integer)
    gender_id: Mapped[int | None] = mapped_column("GenderID", Integer)
    person_id: Mapped[str | None] = mapped_column("PersonID", String)
    flagged: Mapped[bool | None] = mapped_column("Flagged", Boolean, default=False)
    flag_reason: Mapped[str | None] = mapped_column("FlagReason", Text)

    case: Mapped[CaseMaster] = relationship(back_populates="accused")
    arrest_surrenders: Mapped[list[ArrestSurrender]] = relationship(
        back_populates="accused",
        foreign_keys="ArrestSurrender.accused_master_id",
    )
    arrest_surrender_links: Mapped[list[InvArrestSurrenderAccused]] = relationship(
        back_populates="accused"
    )


class ArrestSurrender(Base):
    __tablename__ = "ArrestSurrender"
    __table_args__ = (
        Index("ix_ArrestSurrender_location", "ArrestSurrenderStateId", "ArrestSurrenderDistrictId"),
    )

    arrest_surrender_id: Mapped[int] = mapped_column(
        "ArrestSurrenderID", Integer, primary_key=True, autoincrement=False
    )
    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    arrest_surrender_type_id: Mapped[int | None] = mapped_column(
        "ArrestSurrenderTypeID", Integer
    )
    arrest_surrender_date: Mapped[date | None] = mapped_column(
        "ArrestSurrenderDate", Date
    )
    arrest_surrender_state_id: Mapped[int | None] = mapped_column(
        "ArrestSurrenderStateId", ForeignKey("State.StateID"), index=True
    )
    arrest_surrender_district_id: Mapped[int | None] = mapped_column(
        "ArrestSurrenderDistrictId", ForeignKey("District.DistrictID"), index=True
    )
    police_station_id: Mapped[int | None] = mapped_column(
        "PoliceStationID", ForeignKey("Unit.UnitID"), index=True
    )
    io_id: Mapped[int | None] = mapped_column(
        "IOID", ForeignKey("Employee.EmployeeID"), index=True
    )
    court_id: Mapped[int | None] = mapped_column(
        "CourtID", ForeignKey("Court.CourtID"), index=True
    )
    accused_master_id: Mapped[int | None] = mapped_column(
        "AccusedMasterID", ForeignKey("Accused.AccusedMasterID"), index=True
    )
    is_accused: Mapped[bool | None] = mapped_column("IsAccused", Boolean)
    is_complainant_accused: Mapped[bool | None] = mapped_column(
        "IsComplainantAccused", Boolean
    )

    case: Mapped[CaseMaster] = relationship(back_populates="arrest_surrenders")
    state: Mapped[State | None] = relationship(back_populates="arrest_surrenders")
    district: Mapped[District | None] = relationship(back_populates="arrest_surrenders")
    police_station: Mapped[Unit | None] = relationship(back_populates="arrest_surrenders")
    io: Mapped[Employee | None] = relationship(
        back_populates="arrest_surrenders_as_io",
        foreign_keys=[io_id],
    )
    court: Mapped[Court | None] = relationship(back_populates="arrest_surrenders")
    accused: Mapped[Accused | None] = relationship(
        back_populates="arrest_surrenders",
        foreign_keys=[accused_master_id],
    )
    accused_links: Mapped[list[InvArrestSurrenderAccused]] = relationship(
        back_populates="arrest_surrender"
    )


class InvArrestSurrenderAccused(Base):
    __tablename__ = "inv_arrestsurrenderaccused"

    arrest_surrender_id: Mapped[int] = mapped_column(
        "ArrestSurrenderID",
        ForeignKey("ArrestSurrender.ArrestSurrenderID"),
        primary_key=True,
    )
    accused_master_id: Mapped[int] = mapped_column(
        "AccusedMasterID",
        ForeignKey("Accused.AccusedMasterID"),
        primary_key=True,
    )

    arrest_surrender: Mapped[ArrestSurrender] = relationship(
        back_populates="accused_links"
    )
    accused: Mapped[Accused] = relationship(back_populates="arrest_surrender_links")


class CrimeHeadActSection(Base):
    __tablename__ = "CrimeHeadActSection"
    __table_args__ = (Index("ix_CrimeHeadActSection_ActCode_SectionCode", "ActCode", "SectionCode"),)

    crime_head_id: Mapped[int] = mapped_column(
        "CrimeHeadID",
        ForeignKey("CrimeHead.CrimeHeadID"),
        primary_key=True,
    )
    act_code: Mapped[str] = mapped_column(
        "ActCode", ForeignKey("Act.ActCode"), primary_key=True
    )
    section_code: Mapped[str] = mapped_column(
        "SectionCode", ForeignKey("Section.SectionCode"), primary_key=True
    )

    crime_head: Mapped[CrimeHead] = relationship(back_populates="act_sections")
    act: Mapped[Act] = relationship(back_populates="crime_head_associations")
    section: Mapped[Section] = relationship(back_populates="crime_head_associations")


class ChargesheetDetails(Base):
    __tablename__ = "ChargesheetDetails"

    cs_id: Mapped[int] = mapped_column(
        "CSID", Integer, primary_key=True, autoincrement=False
    )
    case_master_id: Mapped[int] = mapped_column(
        "CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), index=True
    )
    cs_date: Mapped[datetime | None] = mapped_column("csdate", DateTime)
    cs_type: Mapped[str | None] = mapped_column("cstype", CHAR(1))
    police_person_id: Mapped[int | None] = mapped_column(
        "PolicePersonID", ForeignKey("Employee.EmployeeID"), index=True
    )

    case: Mapped[CaseMaster] = relationship(back_populates="chargesheets")
    police_person: Mapped[Employee | None] = relationship(back_populates="chargesheets")


class Vehicle(Base):
    __tablename__ = "Vehicle"

    vehicle_id: Mapped[int] = mapped_column(
        "VehicleID", Integer, primary_key=True, autoincrement=True
    )
    registration_number: Mapped[str] = mapped_column(
        "RegistrationNumber", String, index=True
    )
    owner_accused_id: Mapped[int | None] = mapped_column(
        "OwnerAccusedID", ForeignKey("Accused.AccusedMasterID"), index=True
    )
    active: Mapped[bool | None] = mapped_column("Active", Boolean, default=True)

    owner: Mapped[Accused | None] = relationship(foreign_keys=[owner_accused_id])


class CellTower(Base):
    __tablename__ = "CellTower"

    cell_tower_id: Mapped[int] = mapped_column(
        "CellTowerID", Integer, primary_key=True, autoincrement=True
    )
    tower_code: Mapped[str] = mapped_column("TowerCode", String, index=True)
    latitude: Mapped[Decimal | None] = mapped_column("latitude", Numeric)
    longitude: Mapped[Decimal | None] = mapped_column("longitude", Numeric)
    district_id: Mapped[int | None] = mapped_column(
        "DistrictID", ForeignKey("District.DistrictID"), index=True
    )


class ANPRSighting(Base):
    __tablename__ = "ANPRSighting"

    anpr_sighting_id: Mapped[int] = mapped_column(
        "ANPRSightingID", Integer, primary_key=True, autoincrement=True
    )
    vehicle_id: Mapped[int] = mapped_column(
        "VehicleID", ForeignKey("Vehicle.VehicleID"), index=True
    )
    camera_location: Mapped[str | None] = mapped_column("CameraLocation", String)
    sighting_date_time: Mapped[datetime] = mapped_column(
        "SightingDateTime", DateTime, index=True
    )
    latitude: Mapped[Decimal | None] = mapped_column("latitude", Numeric)
    longitude: Mapped[Decimal | None] = mapped_column("longitude", Numeric)

    vehicle: Mapped[Vehicle] = relationship()


class CDRRecord(Base):
    __tablename__ = "CDRRecord"

    cdr_record_id: Mapped[int] = mapped_column(
        "CDRRecordID", Integer, primary_key=True, autoincrement=True
    )
    accused_master_id: Mapped[int] = mapped_column(
        "AccusedMasterID", ForeignKey("Accused.AccusedMasterID"), index=True
    )
    cell_tower_id: Mapped[int] = mapped_column(
        "CellTowerID", ForeignKey("CellTower.CellTowerID"), index=True
    )
    call_date_time: Mapped[datetime] = mapped_column(
        "CallDateTime", DateTime, index=True
    )
    duration_seconds: Mapped[int] = mapped_column("DurationSeconds", Integer)
    connected_accused_id: Mapped[int | None] = mapped_column(
        "ConnectedAccusedID", ForeignKey("Accused.AccusedMasterID"), index=True
    )

    accused: Mapped[Accused] = relationship(foreign_keys=[accused_master_id])
    connected_accused: Mapped[Accused | None] = relationship(
        foreign_keys=[connected_accused_id]
    )
    cell_tower: Mapped[CellTower] = relationship()


class BiometricMatch(Base):
    __tablename__ = "BiometricMatch"

    biometric_match_id: Mapped[int] = mapped_column(
        "BiometricMatchID", Integer, primary_key=True, autoincrement=True
    )
    accused_master_id: Mapped[int] = mapped_column(
        "AccusedMasterID", ForeignKey("Accused.AccusedMasterID"), index=True
    )
    location_name: Mapped[str | None] = mapped_column("LocationName", String)
    match_date_time: Mapped[datetime] = mapped_column(
        "MatchDateTime", DateTime, index=True
    )
    match_type: Mapped[str] = mapped_column("MatchType", String)
    confidence_score: Mapped[Decimal] = mapped_column("ConfidenceScore", Numeric)

    accused: Mapped[Accused] = relationship()


class FinancialTransaction(Base):
    __tablename__ = "FinancialTransaction"

    financial_transaction_id: Mapped[int] = mapped_column(
        "FinancialTransactionID", Integer, primary_key=True, autoincrement=True
    )
    from_accused_id: Mapped[int] = mapped_column(
        "FromAccusedID", ForeignKey("Accused.AccusedMasterID"), index=True
    )
    to_accused_id: Mapped[int] = mapped_column(
        "ToAccusedID", ForeignKey("Accused.AccusedMasterID"), index=True
    )
    amount: Mapped[Decimal] = mapped_column("Amount", Numeric)
    transaction_date: Mapped[datetime] = mapped_column(
        "TransactionDate", DateTime, index=True
    )

    from_accused: Mapped[Accused] = relationship(foreign_keys=[from_accused_id])
    to_accused: Mapped[Accused] = relationship(foreign_keys=[to_accused_id])


class RelationshipTypeMaster(Base):
    __tablename__ = "RelationshipTypeMaster"

    relationship_type_id: Mapped[int] = mapped_column(
        "RelationshipTypeID", Integer, primary_key=True
    )
    relationship_type_name: Mapped[str] = mapped_column(
        "RelationshipTypeName", String
    )


class AssociationEdge(Base):
    __tablename__ = "AssociationEdge"

    association_edge_id: Mapped[int] = mapped_column(
        "AssociationEdgeID", Integer, primary_key=True, autoincrement=True
    )
    source_entity_type: Mapped[str] = mapped_column("SourceEntityType", String)
    source_entity_id: Mapped[str] = mapped_column("SourceEntityID", String)
    target_entity_type: Mapped[str] = mapped_column("TargetEntityType", String)
    target_entity_id: Mapped[str] = mapped_column("TargetEntityID", String)
    relationship_type_id: Mapped[int] = mapped_column(
        "RelationshipTypeID",
        ForeignKey("RelationshipTypeMaster.RelationshipTypeID"),
        index=True,
    )
    evidence: Mapped[str | None] = mapped_column("Evidence", UnicodeText)
    duration_seconds: Mapped[int | None] = mapped_column(
        "DurationSeconds", Integer
    )

    relationship_type: Mapped[RelationshipTypeMaster] = relationship()


class Notification(Base):
    __tablename__ = "Notification"

    notification_id: Mapped[int] = mapped_column("NotificationID", Integer, primary_key=True, autoincrement=True)
    station_name: Mapped[str] = mapped_column("StationName", String(200))
    message: Mapped[str] = mapped_column("Message", Text)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow)
    thread_id: Mapped[str | None] = mapped_column("ThreadID", String(50), nullable=True)


class CaseNote(Base):
    __tablename__ = "CaseNote"

    case_note_id: Mapped[int] = mapped_column("CaseNoteID", Integer, primary_key=True, autoincrement=True)
    case_master_id: Mapped[int] = mapped_column("CaseMasterID", ForeignKey("CaseMaster.CaseMasterID"), index=True)
    note: Mapped[str] = mapped_column("Note", Text)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=datetime.utcnow)
    added_by_employee_id: Mapped[int | None] = mapped_column("AddedByEmployeeID", ForeignKey("Employee.EmployeeID"), index=True, nullable=True)

    case: Mapped[CaseMaster] = relationship()
    added_by: Mapped[Employee | None] = relationship()


