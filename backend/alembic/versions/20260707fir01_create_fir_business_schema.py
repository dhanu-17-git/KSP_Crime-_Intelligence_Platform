"""create fir business schema

Revision ID: 20260707fir01
Revises: 
Create Date: 2026-07-07 14:35:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260707fir01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "Act",
        sa.Column("ActCode", sa.String(), nullable=False),
        sa.Column("ActDescription", sa.String(), nullable=True),
        sa.Column("ShortName", sa.String(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("ActCode"),
    )
    op.create_table(
        "CaseCategory",
        sa.Column("CaseCategoryID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("LookupValue", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("CaseCategoryID"),
    )
    op.create_table(
        "CaseStatusMaster",
        sa.Column("CaseStatusID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CaseStatusName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("CaseStatusID"),
    )
    op.create_table(
        "CasteMaster",
        sa.Column("caste_master_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("caste_master_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("caste_master_id"),
    )
    op.create_table(
        "CrimeHead",
        sa.Column("CrimeHeadID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CrimeGroupName", sa.String(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("CrimeHeadID"),
    )
    op.create_table(
        "Designation",
        sa.Column("DesignationID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("DesignationName", sa.String(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.Column("SortOrder", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("DesignationID"),
    )
    op.create_table(
        "GravityOffence",
        sa.Column("GravityOffenceID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("LookupValue", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("GravityOffenceID"),
    )
    op.create_table(
        "OccupationMaster",
        sa.Column("OccupationID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("OccupationName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("OccupationID"),
    )
    op.create_table(
        "Rank",
        sa.Column("RankID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("RankName", sa.String(), nullable=True),
        sa.Column("Hierarchy", sa.Integer(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("RankID"),
    )
    op.create_table(
        "ReligionMaster",
        sa.Column("ReligionID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("ReligionName", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("ReligionID"),
    )
    op.create_table(
        "State",
        sa.Column("StateID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("StateName", sa.String(), nullable=True),
        sa.Column("NationalityID", sa.Integer(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("StateID"),
    )
    op.create_table(
        "UnitType",
        sa.Column("UnitTypeID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("UnitTypeName", sa.String(), nullable=True),
        sa.Column("CityDistState", sa.String(), nullable=True),
        sa.Column("Hierarchy", sa.Integer(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("UnitTypeID"),
    )
    op.create_table(
        "CrimeSubHead",
        sa.Column("CrimeSubHeadID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CrimeHeadID", sa.Integer(), nullable=True),
        sa.Column("CrimeHeadName", sa.String(), nullable=True),
        sa.Column("SeqID", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["CrimeHeadID"], ["CrimeHead.CrimeHeadID"]),
        sa.PrimaryKeyConstraint("CrimeSubHeadID"),
    )
    op.create_index(
        op.f("ix_CrimeSubHead_CrimeHeadID"),
        "CrimeSubHead",
        ["CrimeHeadID"],
        unique=False,
    )
    op.create_table(
        "District",
        sa.Column("DistrictID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("DistrictName", sa.String(), nullable=True),
        sa.Column("StateID", sa.Integer(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["StateID"], ["State.StateID"]),
        sa.PrimaryKeyConstraint("DistrictID"),
    )
    op.create_index(
        op.f("ix_District_StateID"), "District", ["StateID"], unique=False
    )
    op.create_table(
        "Section",
        sa.Column("SectionCode", sa.String(), nullable=False),
        sa.Column("ActCode", sa.String(), nullable=True),
        sa.Column("SectionDescription", sa.String(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["ActCode"], ["Act.ActCode"]),
        sa.PrimaryKeyConstraint("SectionCode"),
    )
    op.create_index(op.f("ix_Section_ActCode"), "Section", ["ActCode"], unique=False)
    op.create_table(
        "Court",
        sa.Column("CourtID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CourtName", sa.String(), nullable=True),
        sa.Column("DistrictID", sa.Integer(), nullable=True),
        sa.Column("StateID", sa.Integer(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["DistrictID"], ["District.DistrictID"]),
        sa.ForeignKeyConstraint(["StateID"], ["State.StateID"]),
        sa.PrimaryKeyConstraint("CourtID"),
    )
    op.create_index(op.f("ix_Court_DistrictID"), "Court", ["DistrictID"], unique=False)
    op.create_index(op.f("ix_Court_StateID"), "Court", ["StateID"], unique=False)
    op.create_index(
        "ix_Court_StateID_DistrictID",
        "Court",
        ["StateID", "DistrictID"],
        unique=False,
    )
    op.create_table(
        "CrimeHeadActSection",
        sa.Column("CrimeHeadID", sa.Integer(), nullable=False),
        sa.Column("ActCode", sa.String(), nullable=False),
        sa.Column("SectionCode", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["ActCode"], ["Act.ActCode"]),
        sa.ForeignKeyConstraint(["CrimeHeadID"], ["CrimeHead.CrimeHeadID"]),
        sa.ForeignKeyConstraint(["SectionCode"], ["Section.SectionCode"]),
        sa.PrimaryKeyConstraint("CrimeHeadID", "ActCode", "SectionCode"),
    )
    op.create_index(
        "ix_CrimeHeadActSection_ActCode_SectionCode",
        "CrimeHeadActSection",
        ["ActCode", "SectionCode"],
        unique=False,
    )
    op.create_table(
        "Unit",
        sa.Column("UnitID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("UnitName", sa.String(), nullable=True),
        sa.Column("TypeID", sa.Integer(), nullable=True),
        sa.Column("ParentUnit", sa.Integer(), nullable=True),
        sa.Column("NationalityID", sa.Integer(), nullable=True),
        sa.Column("StateID", sa.Integer(), nullable=True),
        sa.Column("DistrictID", sa.Integer(), nullable=True),
        sa.Column("Active", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["DistrictID"], ["District.DistrictID"]),
        sa.ForeignKeyConstraint(["ParentUnit"], ["Unit.UnitID"]),
        sa.ForeignKeyConstraint(["StateID"], ["State.StateID"]),
        sa.ForeignKeyConstraint(["TypeID"], ["UnitType.UnitTypeID"]),
        sa.PrimaryKeyConstraint("UnitID"),
    )
    op.create_index(op.f("ix_Unit_DistrictID"), "Unit", ["DistrictID"], unique=False)
    op.create_index(op.f("ix_Unit_ParentUnit"), "Unit", ["ParentUnit"], unique=False)
    op.create_index(op.f("ix_Unit_StateID"), "Unit", ["StateID"], unique=False)
    op.create_index(
        "ix_Unit_StateID_DistrictID",
        "Unit",
        ["StateID", "DistrictID"],
        unique=False,
    )
    op.create_index(op.f("ix_Unit_TypeID"), "Unit", ["TypeID"], unique=False)
    op.create_table(
        "Employee",
        sa.Column("EmployeeID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("DistrictID", sa.Integer(), nullable=True),
        sa.Column("UnitID", sa.Integer(), nullable=True),
        sa.Column("RankID", sa.Integer(), nullable=True),
        sa.Column("DesignationID", sa.Integer(), nullable=True),
        sa.Column("KGID", sa.String(), nullable=True),
        sa.Column("FirstName", sa.String(), nullable=True),
        sa.Column("EmployeeDOB", sa.Date(), nullable=True),
        sa.Column("GenderID", sa.Integer(), nullable=True),
        sa.Column("BloodGroupID", sa.Integer(), nullable=True),
        sa.Column("PhysicallyChallenged", sa.Boolean(), nullable=True),
        sa.Column("AppointmentDate", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["DesignationID"], ["Designation.DesignationID"]),
        sa.ForeignKeyConstraint(["DistrictID"], ["District.DistrictID"]),
        sa.ForeignKeyConstraint(["RankID"], ["Rank.RankID"]),
        sa.ForeignKeyConstraint(["UnitID"], ["Unit.UnitID"]),
        sa.PrimaryKeyConstraint("EmployeeID"),
        sa.UniqueConstraint("KGID"),
    )
    op.create_index(
        op.f("ix_Employee_DesignationID"),
        "Employee",
        ["DesignationID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_Employee_DistrictID"), "Employee", ["DistrictID"], unique=False
    )
    op.create_index(op.f("ix_Employee_RankID"), "Employee", ["RankID"], unique=False)
    op.create_index(op.f("ix_Employee_UnitID"), "Employee", ["UnitID"], unique=False)
    op.create_table(
        "CaseMaster",
        sa.Column("CaseMasterID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CrimeNo", sa.String(), nullable=True),
        sa.Column("CaseNo", sa.String(), nullable=True),
        sa.Column("CrimeRegisteredDate", sa.Date(), nullable=True),
        sa.Column("PolicePersonID", sa.Integer(), nullable=True),
        sa.Column("PoliceStationID", sa.Integer(), nullable=True),
        sa.Column("CaseCategoryID", sa.Integer(), nullable=True),
        sa.Column("GravityOffenceID", sa.Integer(), nullable=True),
        sa.Column("CrimeMajorHeadID", sa.Integer(), nullable=True),
        sa.Column("CrimeMinorHeadID", sa.Integer(), nullable=True),
        sa.Column("CaseStatusID", sa.Integer(), nullable=True),
        sa.Column("CourtID", sa.Integer(), nullable=True),
        sa.Column("IncidentFromDate", sa.DateTime(), nullable=True),
        sa.Column("IncidentToDate", sa.DateTime(), nullable=True),
        sa.Column("InfoReceivedPSDate", sa.DateTime(), nullable=True),
        sa.Column("latitude", sa.Numeric(), nullable=True),
        sa.Column("longitude", sa.Numeric(), nullable=True),
        sa.Column("BriefFacts", sa.UnicodeText(), nullable=True),
        sa.ForeignKeyConstraint(["CaseCategoryID"], ["CaseCategory.CaseCategoryID"]),
        sa.ForeignKeyConstraint(["CaseStatusID"], ["CaseStatusMaster.CaseStatusID"]),
        sa.ForeignKeyConstraint(["CourtID"], ["Court.CourtID"]),
        sa.ForeignKeyConstraint(["CrimeMajorHeadID"], ["CrimeHead.CrimeHeadID"]),
        sa.ForeignKeyConstraint(["CrimeMinorHeadID"], ["CrimeSubHead.CrimeSubHeadID"]),
        sa.ForeignKeyConstraint(["GravityOffenceID"], ["GravityOffence.GravityOffenceID"]),
        sa.ForeignKeyConstraint(["PolicePersonID"], ["Employee.EmployeeID"]),
        sa.ForeignKeyConstraint(["PoliceStationID"], ["Unit.UnitID"]),
        sa.PrimaryKeyConstraint("CaseMasterID"),
        sa.UniqueConstraint("CrimeNo", name="uq_CaseMaster_CrimeNo"),
        sa.UniqueConstraint(
            "PoliceStationID",
            "CaseCategoryID",
            "CaseNo",
            name="uq_CaseMaster_station_category_case_no",
        ),
    )
    op.create_index(
        op.f("ix_CaseMaster_CaseCategoryID"),
        "CaseMaster",
        ["CaseCategoryID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_CaseMaster_CaseStatusID"),
        "CaseMaster",
        ["CaseStatusID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_CaseMaster_CourtID"), "CaseMaster", ["CourtID"], unique=False
    )
    op.create_index(
        op.f("ix_CaseMaster_CrimeMajorHeadID"),
        "CaseMaster",
        ["CrimeMajorHeadID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_CaseMaster_CrimeMinorHeadID"),
        "CaseMaster",
        ["CrimeMinorHeadID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_CaseMaster_GravityOffenceID"),
        "CaseMaster",
        ["GravityOffenceID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_CaseMaster_PolicePersonID"),
        "CaseMaster",
        ["PolicePersonID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_CaseMaster_PoliceStationID"),
        "CaseMaster",
        ["PoliceStationID"],
        unique=False,
    )
    op.create_index(
        "ix_CaseMaster_crime_heads",
        "CaseMaster",
        ["CrimeMajorHeadID", "CrimeMinorHeadID"],
        unique=False,
    )
    op.create_index(
        "ix_CaseMaster_registered_station",
        "CaseMaster",
        ["PoliceStationID", "CrimeRegisteredDate"],
        unique=False,
    )
    op.create_table(
        "Accused",
        sa.Column("AccusedMasterID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.Column("AccusedName", sa.String(), nullable=True),
        sa.Column("AgeYear", sa.Integer(), nullable=True),
        sa.Column("GenderID", sa.Integer(), nullable=True),
        sa.Column("PersonID", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.PrimaryKeyConstraint("AccusedMasterID"),
    )
    op.create_index(
        op.f("ix_Accused_CaseMasterID"), "Accused", ["CaseMasterID"], unique=False
    )
    op.create_table(
        "ActSectionAssociation",
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.Column("ActID", sa.String(), nullable=False),
        sa.Column("SectionID", sa.String(), nullable=False),
        sa.Column("ActOrderID", sa.Integer(), nullable=True),
        sa.Column("SectionOrderID", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["ActID"], ["Act.ActCode"]),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.ForeignKeyConstraint(["SectionID"], ["Section.SectionCode"]),
        sa.PrimaryKeyConstraint("CaseMasterID", "ActID", "SectionID"),
    )
    op.create_index(
        "ix_ActSectionAssociation_ActID_SectionID",
        "ActSectionAssociation",
        ["ActID", "SectionID"],
        unique=False,
    )
    op.create_table(
        "ChargesheetDetails",
        sa.Column("CSID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.Column("csdate", sa.DateTime(), nullable=True),
        sa.Column("cstype", sa.CHAR(length=1), nullable=True),
        sa.Column("PolicePersonID", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.ForeignKeyConstraint(["PolicePersonID"], ["Employee.EmployeeID"]),
        sa.PrimaryKeyConstraint("CSID"),
    )
    op.create_index(
        op.f("ix_ChargesheetDetails_CaseMasterID"),
        "ChargesheetDetails",
        ["CaseMasterID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ChargesheetDetails_PolicePersonID"),
        "ChargesheetDetails",
        ["PolicePersonID"],
        unique=False,
    )
    op.create_table(
        "ComplainantDetails",
        sa.Column("ComplainantID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.Column("ComplainantName", sa.String(), nullable=True),
        sa.Column("AgeYear", sa.Integer(), nullable=True),
        sa.Column("OccupationID", sa.Integer(), nullable=True),
        sa.Column("ReligionID", sa.Integer(), nullable=True),
        sa.Column("CasteID", sa.Integer(), nullable=True),
        sa.Column("GenderID", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.ForeignKeyConstraint(["CasteID"], ["CasteMaster.caste_master_id"]),
        sa.ForeignKeyConstraint(["OccupationID"], ["OccupationMaster.OccupationID"]),
        sa.ForeignKeyConstraint(["ReligionID"], ["ReligionMaster.ReligionID"]),
        sa.PrimaryKeyConstraint("ComplainantID"),
    )
    op.create_index(
        op.f("ix_ComplainantDetails_CaseMasterID"),
        "ComplainantDetails",
        ["CaseMasterID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ComplainantDetails_CasteID"),
        "ComplainantDetails",
        ["CasteID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ComplainantDetails_OccupationID"),
        "ComplainantDetails",
        ["OccupationID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ComplainantDetails_ReligionID"),
        "ComplainantDetails",
        ["ReligionID"],
        unique=False,
    )
    op.create_table(
        "Inv_OccuranceTime",
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.PrimaryKeyConstraint("CaseMasterID"),
    )
    op.create_table(
        "Victim",
        sa.Column("VictimMasterID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.Column("VictimName", sa.String(), nullable=True),
        sa.Column("AgeYear", sa.Integer(), nullable=True),
        sa.Column("GenderID", sa.Integer(), nullable=True),
        sa.Column("VictimPolice", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.PrimaryKeyConstraint("VictimMasterID"),
    )
    op.create_index(
        op.f("ix_Victim_CaseMasterID"), "Victim", ["CaseMasterID"], unique=False
    )
    op.create_table(
        "ArrestSurrender",
        sa.Column("ArrestSurrenderID", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("CaseMasterID", sa.Integer(), nullable=False),
        sa.Column("ArrestSurrenderTypeID", sa.Integer(), nullable=True),
        sa.Column("ArrestSurrenderDate", sa.Date(), nullable=True),
        sa.Column("ArrestSurrenderStateId", sa.Integer(), nullable=True),
        sa.Column("ArrestSurrenderDistrictId", sa.Integer(), nullable=True),
        sa.Column("PoliceStationID", sa.Integer(), nullable=True),
        sa.Column("IOID", sa.Integer(), nullable=True),
        sa.Column("CourtID", sa.Integer(), nullable=True),
        sa.Column("AccusedMasterID", sa.Integer(), nullable=True),
        sa.Column("IsAccused", sa.Boolean(), nullable=True),
        sa.Column("IsComplainantAccused", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["AccusedMasterID"], ["Accused.AccusedMasterID"]),
        sa.ForeignKeyConstraint(["ArrestSurrenderDistrictId"], ["District.DistrictID"]),
        sa.ForeignKeyConstraint(["ArrestSurrenderStateId"], ["State.StateID"]),
        sa.ForeignKeyConstraint(["CaseMasterID"], ["CaseMaster.CaseMasterID"]),
        sa.ForeignKeyConstraint(["CourtID"], ["Court.CourtID"]),
        sa.ForeignKeyConstraint(["IOID"], ["Employee.EmployeeID"]),
        sa.ForeignKeyConstraint(["PoliceStationID"], ["Unit.UnitID"]),
        sa.PrimaryKeyConstraint("ArrestSurrenderID"),
    )
    op.create_index(
        op.f("ix_ArrestSurrender_AccusedMasterID"),
        "ArrestSurrender",
        ["AccusedMasterID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ArrestSurrender_ArrestSurrenderDistrictId"),
        "ArrestSurrender",
        ["ArrestSurrenderDistrictId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ArrestSurrender_ArrestSurrenderStateId"),
        "ArrestSurrender",
        ["ArrestSurrenderStateId"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ArrestSurrender_CaseMasterID"),
        "ArrestSurrender",
        ["CaseMasterID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ArrestSurrender_CourtID"),
        "ArrestSurrender",
        ["CourtID"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ArrestSurrender_IOID"), "ArrestSurrender", ["IOID"], unique=False
    )
    op.create_index(
        op.f("ix_ArrestSurrender_PoliceStationID"),
        "ArrestSurrender",
        ["PoliceStationID"],
        unique=False,
    )
    op.create_index(
        "ix_ArrestSurrender_location",
        "ArrestSurrender",
        ["ArrestSurrenderStateId", "ArrestSurrenderDistrictId"],
        unique=False,
    )
    op.create_table(
        "inv_arrestsurrenderaccused",
        sa.Column("ArrestSurrenderID", sa.Integer(), nullable=False),
        sa.Column("AccusedMasterID", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["AccusedMasterID"], ["Accused.AccusedMasterID"]),
        sa.ForeignKeyConstraint(
            ["ArrestSurrenderID"], ["ArrestSurrender.ArrestSurrenderID"]
        ),
        sa.PrimaryKeyConstraint("ArrestSurrenderID", "AccusedMasterID"),
    )


def downgrade() -> None:
    op.drop_table("inv_arrestsurrenderaccused")
    op.drop_index("ix_ArrestSurrender_location", table_name="ArrestSurrender")
    op.drop_index(op.f("ix_ArrestSurrender_PoliceStationID"), table_name="ArrestSurrender")
    op.drop_index(op.f("ix_ArrestSurrender_IOID"), table_name="ArrestSurrender")
    op.drop_index(op.f("ix_ArrestSurrender_CourtID"), table_name="ArrestSurrender")
    op.drop_index(op.f("ix_ArrestSurrender_CaseMasterID"), table_name="ArrestSurrender")
    op.drop_index(
        op.f("ix_ArrestSurrender_ArrestSurrenderStateId"),
        table_name="ArrestSurrender",
    )
    op.drop_index(
        op.f("ix_ArrestSurrender_ArrestSurrenderDistrictId"),
        table_name="ArrestSurrender",
    )
    op.drop_index(op.f("ix_ArrestSurrender_AccusedMasterID"), table_name="ArrestSurrender")
    op.drop_table("ArrestSurrender")
    op.drop_index(op.f("ix_Victim_CaseMasterID"), table_name="Victim")
    op.drop_table("Victim")
    op.drop_table("Inv_OccuranceTime")
    op.drop_index(
        op.f("ix_ComplainantDetails_ReligionID"),
        table_name="ComplainantDetails",
    )
    op.drop_index(
        op.f("ix_ComplainantDetails_OccupationID"),
        table_name="ComplainantDetails",
    )
    op.drop_index(op.f("ix_ComplainantDetails_CasteID"), table_name="ComplainantDetails")
    op.drop_index(
        op.f("ix_ComplainantDetails_CaseMasterID"),
        table_name="ComplainantDetails",
    )
    op.drop_table("ComplainantDetails")
    op.drop_index(
        op.f("ix_ChargesheetDetails_PolicePersonID"),
        table_name="ChargesheetDetails",
    )
    op.drop_index(
        op.f("ix_ChargesheetDetails_CaseMasterID"),
        table_name="ChargesheetDetails",
    )
    op.drop_table("ChargesheetDetails")
    op.drop_index(
        "ix_ActSectionAssociation_ActID_SectionID",
        table_name="ActSectionAssociation",
    )
    op.drop_table("ActSectionAssociation")
    op.drop_index(op.f("ix_Accused_CaseMasterID"), table_name="Accused")
    op.drop_table("Accused")
    op.drop_index("ix_CaseMaster_registered_station", table_name="CaseMaster")
    op.drop_index("ix_CaseMaster_crime_heads", table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_PoliceStationID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_PolicePersonID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_GravityOffenceID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_CrimeMinorHeadID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_CrimeMajorHeadID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_CourtID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_CaseStatusID"), table_name="CaseMaster")
    op.drop_index(op.f("ix_CaseMaster_CaseCategoryID"), table_name="CaseMaster")
    op.drop_table("CaseMaster")
    op.drop_index(op.f("ix_Employee_UnitID"), table_name="Employee")
    op.drop_index(op.f("ix_Employee_RankID"), table_name="Employee")
    op.drop_index(op.f("ix_Employee_DistrictID"), table_name="Employee")
    op.drop_index(op.f("ix_Employee_DesignationID"), table_name="Employee")
    op.drop_table("Employee")
    op.drop_index(op.f("ix_Unit_TypeID"), table_name="Unit")
    op.drop_index("ix_Unit_StateID_DistrictID", table_name="Unit")
    op.drop_index(op.f("ix_Unit_StateID"), table_name="Unit")
    op.drop_index(op.f("ix_Unit_ParentUnit"), table_name="Unit")
    op.drop_index(op.f("ix_Unit_DistrictID"), table_name="Unit")
    op.drop_table("Unit")
    op.drop_index(
        "ix_CrimeHeadActSection_ActCode_SectionCode",
        table_name="CrimeHeadActSection",
    )
    op.drop_table("CrimeHeadActSection")
    op.drop_index("ix_Court_StateID_DistrictID", table_name="Court")
    op.drop_index(op.f("ix_Court_StateID"), table_name="Court")
    op.drop_index(op.f("ix_Court_DistrictID"), table_name="Court")
    op.drop_table("Court")
    op.drop_index(op.f("ix_Section_ActCode"), table_name="Section")
    op.drop_table("Section")
    op.drop_index(op.f("ix_District_StateID"), table_name="District")
    op.drop_table("District")
    op.drop_index(op.f("ix_CrimeSubHead_CrimeHeadID"), table_name="CrimeSubHead")
    op.drop_table("CrimeSubHead")
    op.drop_table("UnitType")
    op.drop_table("State")
    op.drop_table("ReligionMaster")
    op.drop_table("Rank")
    op.drop_table("OccupationMaster")
    op.drop_table("GravityOffence")
    op.drop_table("Designation")
    op.drop_table("CrimeHead")
    op.drop_table("CasteMaster")
    op.drop_table("CaseStatusMaster")
    op.drop_table("CaseCategory")
    op.drop_table("Act")
