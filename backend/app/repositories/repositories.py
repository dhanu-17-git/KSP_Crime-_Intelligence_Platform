"""Concrete repository implementations for all KSP domain models."""

from __future__ import annotations

from app.models.fir import (
    Accused,
    Act,
    ActSectionAssociation,
    ArrestSurrender,
    CaseCategory,
    CaseMaster,
    CaseStatusMaster,
    CasteMaster,
    ChargesheetDetails,
    ComplainantDetails,
    Court,
    CrimeHead,
    CrimeHeadActSection,
    CrimeSubHead,
    Designation,
    District,
    Employee,
    GravityOffence,
    InvArrestSurrenderAccused,
    InvOccuranceTime,
    OccupationMaster,
    Rank,
    ReligionMaster,
    Section,
    State,
    Unit,
    UnitType,
    Victim,
)
from app.repositories.base import BaseRepository


class StateRepository(BaseRepository[State]):
    model = State
    primary_key = "state_id"
    search_fields = ("state_name",)
    default_sort = "state_id"


class DistrictRepository(BaseRepository[District]):
    model = District
    primary_key = "district_id"
    search_fields = ("district_name",)
    default_sort = "district_id"


class CourtRepository(BaseRepository[Court]):
    model = Court
    primary_key = "court_id"
    search_fields = ("court_name",)
    default_sort = "court_id"


class UnitTypeRepository(BaseRepository[UnitType]):
    model = UnitType
    primary_key = "unit_type_id"
    search_fields = ("unit_type_name",)
    default_sort = "unit_type_id"


class UnitRepository(BaseRepository[Unit]):
    model = Unit
    primary_key = "unit_id"
    search_fields = ("unit_name",)
    default_sort = "unit_id"


class RankRepository(BaseRepository[Rank]):
    model = Rank
    primary_key = "rank_id"
    search_fields = ("rank_name",)
    default_sort = "rank_id"


class DesignationRepository(BaseRepository[Designation]):
    model = Designation
    primary_key = "designation_id"
    search_fields = ("designation_name",)
    default_sort = "designation_id"


class EmployeeRepository(BaseRepository[Employee]):
    model = Employee
    primary_key = "employee_id"
    search_fields = ("first_name", "kgid")
    default_sort = "employee_id"


class CaseCategoryRepository(BaseRepository[CaseCategory]):
    model = CaseCategory
    primary_key = "case_category_id"
    search_fields = ("lookup_value",)
    default_sort = "case_category_id"


class GravityOffenceRepository(BaseRepository[GravityOffence]):
    model = GravityOffence
    primary_key = "gravity_offence_id"
    search_fields = ("lookup_value",)
    default_sort = "gravity_offence_id"


class CrimeHeadRepository(BaseRepository[CrimeHead]):
    model = CrimeHead
    primary_key = "crime_head_id"
    search_fields = ("crime_group_name",)
    default_sort = "crime_head_id"


class CrimeSubHeadRepository(BaseRepository[CrimeSubHead]):
    model = CrimeSubHead
    primary_key = "crime_sub_head_id"
    search_fields = ("crime_head_name",)
    default_sort = "crime_sub_head_id"


class CaseStatusMasterRepository(BaseRepository[CaseStatusMaster]):
    model = CaseStatusMaster
    primary_key = "case_status_id"
    search_fields = ("case_status_name",)
    default_sort = "case_status_id"


class CasteMasterRepository(BaseRepository[CasteMaster]):
    model = CasteMaster
    primary_key = "caste_master_id"
    search_fields = ("caste_master_name",)
    default_sort = "caste_master_id"


class ReligionMasterRepository(BaseRepository[ReligionMaster]):
    model = ReligionMaster
    primary_key = "religion_id"
    search_fields = ("religion_name",)
    default_sort = "religion_id"


class OccupationMasterRepository(BaseRepository[OccupationMaster]):
    model = OccupationMaster
    primary_key = "occupation_id"
    search_fields = ("occupation_name",)
    default_sort = "occupation_id"


class ActRepository(BaseRepository[Act]):
    model = Act
    primary_key = "act_code"
    search_fields = ("act_description", "short_name")
    default_sort = "act_code"


class SectionRepository(BaseRepository[Section]):
    model = Section
    primary_key = "section_code"
    search_fields = ("section_description",)
    default_sort = "section_code"


class CaseMasterRepository(BaseRepository[CaseMaster]):
    model = CaseMaster
    primary_key = "case_master_id"
    search_fields = ("crime_no", "case_no", "brief_facts")
    default_sort = ("case_master_id", True)


class InvOccuranceTimeRepository(BaseRepository[InvOccuranceTime]):
    model = InvOccuranceTime
    primary_key = "case_master_id"
    default_sort = "case_master_id"


class ComplainantDetailsRepository(BaseRepository[ComplainantDetails]):
    model = ComplainantDetails
    primary_key = "complainant_id"
    search_fields = ("complainant_name",)
    default_sort = "complainant_id"


class VictimRepository(BaseRepository[Victim]):
    model = Victim
    primary_key = "victim_master_id"
    search_fields = ("victim_name",)
    default_sort = "victim_master_id"


class AccusedRepository(BaseRepository[Accused]):
    model = Accused
    primary_key = "accused_master_id"
    search_fields = ("accused_name", "person_id")
    default_sort = "accused_master_id"


class ArrestSurrenderRepository(BaseRepository[ArrestSurrender]):
    model = ArrestSurrender
    primary_key = "arrest_surrender_id"
    default_sort = "arrest_surrender_id"


class InvArrestSurrenderAccusedRepository(BaseRepository[InvArrestSurrenderAccused]):
    model = InvArrestSurrenderAccused
    primary_key = ("arrest_surrender_id", "accused_master_id")
    default_sort = "arrest_surrender_id"


class ActSectionAssociationRepository(BaseRepository[ActSectionAssociation]):
    model = ActSectionAssociation
    primary_key = ("case_master_id", "act_id", "section_id")
    default_sort = "case_master_id"


class CrimeHeadActSectionRepository(BaseRepository[CrimeHeadActSection]):
    model = CrimeHeadActSection
    primary_key = ("crime_head_id", "act_code", "section_code")
    default_sort = "crime_head_id"


class ChargesheetDetailsRepository(BaseRepository[ChargesheetDetails]):
    model = ChargesheetDetails
    primary_key = "cs_id"
    default_sort = "cs_id"
