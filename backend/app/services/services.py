"""Concrete service implementations for all KSP domain entities."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

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
from app.repositories.repositories import (
    AccusedRepository,
    ActRepository,
    ActSectionAssociationRepository,
    ArrestSurrenderRepository,
    CaseCategoryRepository,
    CaseMasterRepository,
    CaseStatusMasterRepository,
    CasteMasterRepository,
    ChargesheetDetailsRepository,
    ComplainantDetailsRepository,
    CourtRepository,
    CrimeHeadActSectionRepository,
    CrimeHeadRepository,
    CrimeSubHeadRepository,
    DesignationRepository,
    DistrictRepository,
    EmployeeRepository,
    GravityOffenceRepository,
    InvArrestSurrenderAccusedRepository,
    InvOccuranceTimeRepository,
    OccupationMasterRepository,
    RankRepository,
    ReligionMasterRepository,
    SectionRepository,
    StateRepository,
    UnitRepository,
    UnitTypeRepository,
    VictimRepository,
)
from app.services.base_service import BaseService


# ── Simple lookup / master services ──────────────────────────────────────────

class StateService(BaseService[State, StateRepository]):
    repository_class = StateRepository


class DistrictService(BaseService[District, DistrictRepository]):
    repository_class = DistrictRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(StateRepository(self.session), data.get("state_id"), "State")

    async def _validate_update(self, pk: Any, data: Mapping[str, Any]) -> None:
        if "state_id" in data:
            await self._assert_exists(StateRepository(self.session), data["state_id"], "State")


class CourtService(BaseService[Court, CourtRepository]):
    repository_class = CourtRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(DistrictRepository(self.session), data.get("district_id"), "District")
        await self._assert_exists(StateRepository(self.session), data.get("state_id"), "State")


class UnitTypeService(BaseService[UnitType, UnitTypeRepository]):
    repository_class = UnitTypeRepository


class UnitService(BaseService[Unit, UnitRepository]):
    repository_class = UnitRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(UnitTypeRepository(self.session), data.get("type_id"), "UnitType")
        await self._assert_exists(StateRepository(self.session), data.get("state_id"), "State")
        await self._assert_exists(DistrictRepository(self.session), data.get("district_id"), "District")
        if data.get("parent_unit_id"):
            await self._assert_exists(UnitRepository(self.session), data["parent_unit_id"], "ParentUnit")


class RankService(BaseService[Rank, RankRepository]):
    repository_class = RankRepository


class DesignationService(BaseService[Designation, DesignationRepository]):
    repository_class = DesignationRepository


class EmployeeService(BaseService[Employee, EmployeeRepository]):
    repository_class = EmployeeRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(DistrictRepository(self.session), data.get("district_id"), "District")
        await self._assert_exists(UnitRepository(self.session), data.get("unit_id"), "Unit")
        await self._assert_exists(RankRepository(self.session), data.get("rank_id"), "Rank")
        await self._assert_exists(DesignationRepository(self.session), data.get("designation_id"), "Designation")


class CaseCategoryService(BaseService[CaseCategory, CaseCategoryRepository]):
    repository_class = CaseCategoryRepository


class GravityOffenceService(BaseService[GravityOffence, GravityOffenceRepository]):
    repository_class = GravityOffenceRepository


class CrimeHeadService(BaseService[CrimeHead, CrimeHeadRepository]):
    repository_class = CrimeHeadRepository


class CrimeSubHeadService(BaseService[CrimeSubHead, CrimeSubHeadRepository]):
    repository_class = CrimeSubHeadRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CrimeHeadRepository(self.session), data.get("crime_head_id"), "CrimeHead")


class CaseStatusMasterService(BaseService[CaseStatusMaster, CaseStatusMasterRepository]):
    repository_class = CaseStatusMasterRepository


class CasteMasterService(BaseService[CasteMaster, CasteMasterRepository]):
    repository_class = CasteMasterRepository


class ReligionMasterService(BaseService[ReligionMaster, ReligionMasterRepository]):
    repository_class = ReligionMasterRepository


class OccupationMasterService(BaseService[OccupationMaster, OccupationMasterRepository]):
    repository_class = OccupationMasterRepository


class ActService(BaseService[Act, ActRepository]):
    repository_class = ActRepository


class SectionService(BaseService[Section, SectionRepository]):
    repository_class = SectionRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(ActRepository(self.session), data.get("act_code"), "Act")


# ── Core case / investigation services ───────────────────────────────────────

class CaseMasterService(BaseService[CaseMaster, CaseMasterRepository]):
    repository_class = CaseMasterRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(UnitRepository(self.session), data.get("police_station_id"), "PoliceStation")
        await self._assert_exists(EmployeeRepository(self.session), data.get("police_person_id"), "Employee")
        await self._assert_exists(CaseCategoryRepository(self.session), data.get("case_category_id"), "CaseCategory")
        await self._assert_exists(CaseStatusMasterRepository(self.session), data.get("case_status_id"), "CaseStatus")
        await self._assert_exists(CourtRepository(self.session), data.get("court_id"), "Court")
        await self._assert_exists(CrimeHeadRepository(self.session), data.get("crime_major_head_id"), "CrimeMajorHead")
        await self._assert_exists(CrimeSubHeadRepository(self.session), data.get("crime_minor_head_id"), "CrimeMinorHead")
        await self._assert_exists(GravityOffenceRepository(self.session), data.get("gravity_offence_id"), "GravityOffence")


class InvOccuranceTimeService(BaseService[InvOccuranceTime, InvOccuranceTimeRepository]):
    repository_class = InvOccuranceTimeRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")


class ComplainantDetailsService(BaseService[ComplainantDetails, ComplainantDetailsRepository]):
    repository_class = ComplainantDetailsRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")
        await self._assert_exists(OccupationMasterRepository(self.session), data.get("occupation_id"), "Occupation")
        await self._assert_exists(ReligionMasterRepository(self.session), data.get("religion_id"), "Religion")
        await self._assert_exists(CasteMasterRepository(self.session), data.get("caste_id"), "Caste")


class VictimService(BaseService[Victim, VictimRepository]):
    repository_class = VictimRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")


class AccusedService(BaseService[Accused, AccusedRepository]):
    repository_class = AccusedRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")


class ArrestSurrenderService(BaseService[ArrestSurrender, ArrestSurrenderRepository]):
    repository_class = ArrestSurrenderRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")
        await self._assert_exists(AccusedRepository(self.session), data.get("accused_master_id"), "Accused")
        await self._assert_exists(EmployeeRepository(self.session), data.get("io_id"), "InvestigatingOfficer")
        await self._assert_exists(CourtRepository(self.session), data.get("court_id"), "Court")
        await self._assert_exists(UnitRepository(self.session), data.get("police_station_id"), "PoliceStation")


class InvArrestSurrenderAccusedService(BaseService[InvArrestSurrenderAccused, InvArrestSurrenderAccusedRepository]):
    repository_class = InvArrestSurrenderAccusedRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(ArrestSurrenderRepository(self.session), data.get("arrest_surrender_id"), "ArrestSurrender")
        await self._assert_exists(AccusedRepository(self.session), data.get("accused_master_id"), "Accused")


class ActSectionAssociationService(BaseService[ActSectionAssociation, ActSectionAssociationRepository]):
    repository_class = ActSectionAssociationRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")
        await self._assert_exists(ActRepository(self.session), data.get("act_id"), "Act")
        await self._assert_exists(SectionRepository(self.session), data.get("section_id"), "Section")


class CrimeHeadActSectionService(BaseService[CrimeHeadActSection, CrimeHeadActSectionRepository]):
    repository_class = CrimeHeadActSectionRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CrimeHeadRepository(self.session), data.get("crime_head_id"), "CrimeHead")
        await self._assert_exists(ActRepository(self.session), data.get("act_code"), "Act")
        await self._assert_exists(SectionRepository(self.session), data.get("section_code"), "Section")


class ChargesheetDetailsService(BaseService[ChargesheetDetails, ChargesheetDetailsRepository]):
    repository_class = ChargesheetDetailsRepository

    async def _validate_create(self, data: Mapping[str, Any]) -> None:
        await self._assert_exists(CaseMasterRepository(self.session), data.get("case_master_id"), "CaseMaster")
        await self._assert_exists(EmployeeRepository(self.session), data.get("police_person_id"), "Employee")
