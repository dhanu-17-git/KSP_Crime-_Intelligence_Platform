from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveID = Annotated[int, Field(gt=0)]
AgeYear = Annotated[int, Field(ge=0, le=130)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
CrimeNoStr = Annotated[str, Field(pattern=r"^\d{18}$")]
CaseNoStr = Annotated[str, Field(pattern=r"^\d{9}$")]
Latitude = Annotated[Decimal, Field(ge=Decimal("-90"), le=Decimal("90"))]
Longitude = Annotated[Decimal, Field(ge=Decimal("-180"), le=Decimal("180"))]
PersonOrderStr = Annotated[str, Field(pattern=r"^[A-Za-z]\d+$")]


class SchemaBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ORMBase(SchemaBase):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        str_strip_whitespace=True,
    )


class SearchBase(SchemaBase):
    query: NonEmptyStr | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class DateRangeBase(SchemaBase):
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


class DateTimeRangeBase(SchemaBase):
    datetime_from: datetime | None = None
    datetime_to: datetime | None = None

    @model_validator(mode="after")
    def validate_datetime_range(self) -> Self:
        if self.datetime_from and self.datetime_to and self.datetime_to < self.datetime_from:
            raise ValueError("datetime_to must be greater than or equal to datetime_from")
        return self


class ActiveFilterBase(SchemaBase):
    active: bool | None = None


class StateBase(SchemaBase):
    state_name: NonEmptyStr | None = None
    nationality_id: PositiveID | None = None
    active: bool | None = None


class StateCreate(StateBase):
    state_id: PositiveID


class StateUpdate(StateBase):
    pass


class StateResponse(StateBase, ORMBase):
    state_id: PositiveID


class StateSummary(ORMBase):
    state_id: PositiveID
    state_name: str | None = None
    active: bool | None = None


class StateSearch(SearchBase, ActiveFilterBase):
    state_id: PositiveID | None = None
    nationality_id: PositiveID | None = None


class StateFilter(ActiveFilterBase):
    state_id: PositiveID | None = None
    nationality_id: PositiveID | None = None


class DistrictBase(SchemaBase):
    district_name: NonEmptyStr | None = None
    state_id: PositiveID | None = None
    active: bool | None = None


class DistrictCreate(DistrictBase):
    district_id: PositiveID


class DistrictUpdate(DistrictBase):
    pass


class DistrictResponse(DistrictBase, ORMBase):
    district_id: PositiveID


class DistrictSummary(ORMBase):
    district_id: PositiveID
    district_name: str | None = None
    state_id: int | None = None
    active: bool | None = None


class DistrictSearch(SearchBase, ActiveFilterBase):
    district_id: PositiveID | None = None
    state_id: PositiveID | None = None


class DistrictFilter(ActiveFilterBase):
    district_id: PositiveID | None = None
    state_id: PositiveID | None = None


class CourtBase(SchemaBase):
    court_name: NonEmptyStr | None = None
    district_id: PositiveID | None = None
    state_id: PositiveID | None = None
    active: bool | None = None


class CourtCreate(CourtBase):
    court_id: PositiveID


class CourtUpdate(CourtBase):
    pass


class CourtResponse(CourtBase, ORMBase):
    court_id: PositiveID


class CourtSummary(ORMBase):
    court_id: PositiveID
    court_name: str | None = None
    district_id: int | None = None
    state_id: int | None = None
    active: bool | None = None


class CourtSearch(SearchBase, ActiveFilterBase):
    court_id: PositiveID | None = None
    district_id: PositiveID | None = None
    state_id: PositiveID | None = None


class CourtFilter(ActiveFilterBase):
    court_id: PositiveID | None = None
    district_id: PositiveID | None = None
    state_id: PositiveID | None = None


class UnitTypeBase(SchemaBase):
    unit_type_name: NonEmptyStr | None = None
    city_dist_state: NonEmptyStr | None = None
    hierarchy: int | None = Field(default=None, ge=0)
    active: bool | None = None


class UnitTypeCreate(UnitTypeBase):
    unit_type_id: PositiveID


class UnitTypeUpdate(UnitTypeBase):
    pass


class UnitTypeResponse(UnitTypeBase, ORMBase):
    unit_type_id: PositiveID


class UnitTypeSummary(ORMBase):
    unit_type_id: PositiveID
    unit_type_name: str | None = None
    hierarchy: int | None = None
    active: bool | None = None


class UnitTypeSearch(SearchBase, ActiveFilterBase):
    unit_type_id: PositiveID | None = None
    city_dist_state: NonEmptyStr | None = None


class UnitTypeFilter(ActiveFilterBase):
    unit_type_id: PositiveID | None = None
    city_dist_state: NonEmptyStr | None = None


class UnitBase(SchemaBase):
    unit_name: NonEmptyStr | None = None
    type_id: PositiveID | None = None
    parent_unit_id: PositiveID | None = None
    nationality_id: PositiveID | None = None
    state_id: PositiveID | None = None
    district_id: PositiveID | None = None
    active: bool | None = None


class UnitCreate(UnitBase):
    unit_id: PositiveID


class UnitUpdate(UnitBase):
    pass


class UnitResponse(UnitBase, ORMBase):
    unit_id: PositiveID


class UnitSummary(ORMBase):
    unit_id: PositiveID
    unit_name: str | None = None
    type_id: int | None = None
    parent_unit_id: int | None = None
    state_id: int | None = None
    district_id: int | None = None
    active: bool | None = None


class UnitSearch(SearchBase, ActiveFilterBase):
    unit_id: PositiveID | None = None
    type_id: PositiveID | None = None
    parent_unit_id: PositiveID | None = None
    state_id: PositiveID | None = None
    district_id: PositiveID | None = None


class UnitFilter(ActiveFilterBase):
    unit_id: PositiveID | None = None
    type_id: PositiveID | None = None
    parent_unit_id: PositiveID | None = None
    state_id: PositiveID | None = None
    district_id: PositiveID | None = None


class RankBase(SchemaBase):
    rank_name: NonEmptyStr | None = None
    hierarchy: int | None = Field(default=None, ge=0)
    active: bool | None = None


class RankCreate(RankBase):
    rank_id: PositiveID


class RankUpdate(RankBase):
    pass


class RankResponse(RankBase, ORMBase):
    rank_id: PositiveID


class RankSummary(ORMBase):
    rank_id: PositiveID
    rank_name: str | None = None
    hierarchy: int | None = None
    active: bool | None = None


class RankSearch(SearchBase, ActiveFilterBase):
    rank_id: PositiveID | None = None


class RankFilter(ActiveFilterBase):
    rank_id: PositiveID | None = None
    hierarchy: int | None = Field(default=None, ge=0)


class DesignationBase(SchemaBase):
    designation_name: NonEmptyStr | None = None
    active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)


class DesignationCreate(DesignationBase):
    designation_id: PositiveID


class DesignationUpdate(DesignationBase):
    pass


class DesignationResponse(DesignationBase, ORMBase):
    designation_id: PositiveID


class DesignationSummary(ORMBase):
    designation_id: PositiveID
    designation_name: str | None = None
    active: bool | None = None
    sort_order: int | None = None


class DesignationSearch(SearchBase, ActiveFilterBase):
    designation_id: PositiveID | None = None


class DesignationFilter(ActiveFilterBase):
    designation_id: PositiveID | None = None
    sort_order: int | None = Field(default=None, ge=0)


class EmployeeBase(SchemaBase):
    district_id: PositiveID | None = None
    unit_id: PositiveID | None = None
    rank_id: PositiveID | None = None
    designation_id: PositiveID | None = None
    kgid: NonEmptyStr | None = None
    first_name: NonEmptyStr | None = None
    employee_dob: date | None = None
    gender_id: PositiveID | None = None
    blood_group_id: PositiveID | None = None
    physically_challenged: bool | None = None
    appointment_date: date | None = None


class EmployeeCreate(EmployeeBase):
    employee_id: PositiveID


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase, ORMBase):
    employee_id: PositiveID


class EmployeeSummary(ORMBase):
    employee_id: PositiveID
    kgid: str | None = None
    first_name: str | None = None
    district_id: int | None = None
    unit_id: int | None = None
    rank_id: int | None = None
    designation_id: int | None = None


class EmployeeSearch(SearchBase):
    employee_id: PositiveID | None = None
    district_id: PositiveID | None = None
    unit_id: PositiveID | None = None
    rank_id: PositiveID | None = None
    designation_id: PositiveID | None = None


class EmployeeFilter(SchemaBase):
    employee_id: PositiveID | None = None
    district_id: PositiveID | None = None
    unit_id: PositiveID | None = None
    rank_id: PositiveID | None = None
    designation_id: PositiveID | None = None
    gender_id: PositiveID | None = None
    physically_challenged: bool | None = None


class CaseCategoryBase(SchemaBase):
    lookup_value: NonEmptyStr | None = None


class CaseCategoryCreate(CaseCategoryBase):
    case_category_id: PositiveID


class CaseCategoryUpdate(CaseCategoryBase):
    pass


class CaseCategoryResponse(CaseCategoryBase, ORMBase):
    case_category_id: PositiveID


class CaseCategorySummary(ORMBase):
    case_category_id: PositiveID
    lookup_value: str | None = None


class CaseCategorySearch(SearchBase):
    case_category_id: PositiveID | None = None


class CaseCategoryFilter(SchemaBase):
    case_category_id: PositiveID | None = None


class GravityOffenceBase(SchemaBase):
    lookup_value: NonEmptyStr | None = None


class GravityOffenceCreate(GravityOffenceBase):
    gravity_offence_id: PositiveID


class GravityOffenceUpdate(GravityOffenceBase):
    pass


class GravityOffenceResponse(GravityOffenceBase, ORMBase):
    gravity_offence_id: PositiveID


class GravityOffenceSummary(ORMBase):
    gravity_offence_id: PositiveID
    lookup_value: str | None = None


class GravityOffenceSearch(SearchBase):
    gravity_offence_id: PositiveID | None = None


class GravityOffenceFilter(SchemaBase):
    gravity_offence_id: PositiveID | None = None


class CrimeHeadBase(SchemaBase):
    crime_group_name: NonEmptyStr | None = None
    active: bool | None = None


class CrimeHeadCreate(CrimeHeadBase):
    crime_head_id: PositiveID


class CrimeHeadUpdate(CrimeHeadBase):
    pass


class CrimeHeadResponse(CrimeHeadBase, ORMBase):
    crime_head_id: PositiveID


class CrimeHeadSummary(ORMBase):
    crime_head_id: PositiveID
    crime_group_name: str | None = None
    active: bool | None = None


class CrimeHeadSearch(SearchBase, ActiveFilterBase):
    crime_head_id: PositiveID | None = None


class CrimeHeadFilter(ActiveFilterBase):
    crime_head_id: PositiveID | None = None


class CrimeSubHeadBase(SchemaBase):
    crime_head_id: PositiveID | None = None
    crime_head_name: NonEmptyStr | None = None
    seq_id: int | None = Field(default=None, ge=0)


class CrimeSubHeadCreate(CrimeSubHeadBase):
    crime_sub_head_id: PositiveID


class CrimeSubHeadUpdate(CrimeSubHeadBase):
    pass


class CrimeSubHeadResponse(CrimeSubHeadBase, ORMBase):
    crime_sub_head_id: PositiveID


class CrimeSubHeadSummary(ORMBase):
    crime_sub_head_id: PositiveID
    crime_head_id: int | None = None
    crime_head_name: str | None = None
    seq_id: int | None = None


class CrimeSubHeadSearch(SearchBase):
    crime_sub_head_id: PositiveID | None = None
    crime_head_id: PositiveID | None = None


class CrimeSubHeadFilter(SchemaBase):
    crime_sub_head_id: PositiveID | None = None
    crime_head_id: PositiveID | None = None
    seq_id: int | None = Field(default=None, ge=0)


class CaseStatusMasterBase(SchemaBase):
    case_status_name: NonEmptyStr | None = None


class CaseStatusMasterCreate(CaseStatusMasterBase):
    case_status_id: PositiveID


class CaseStatusMasterUpdate(CaseStatusMasterBase):
    pass


class CaseStatusMasterResponse(CaseStatusMasterBase, ORMBase):
    case_status_id: PositiveID


class CaseStatusMasterSummary(ORMBase):
    case_status_id: PositiveID
    case_status_name: str | None = None


class CaseStatusMasterSearch(SearchBase):
    case_status_id: PositiveID | None = None


class CaseStatusMasterFilter(SchemaBase):
    case_status_id: PositiveID | None = None


class CasteMasterBase(SchemaBase):
    caste_master_name: NonEmptyStr | None = None


class CasteMasterCreate(CasteMasterBase):
    caste_master_id: PositiveID


class CasteMasterUpdate(CasteMasterBase):
    pass


class CasteMasterResponse(CasteMasterBase, ORMBase):
    caste_master_id: PositiveID


class CasteMasterSummary(ORMBase):
    caste_master_id: PositiveID
    caste_master_name: str | None = None


class CasteMasterSearch(SearchBase):
    caste_master_id: PositiveID | None = None


class CasteMasterFilter(SchemaBase):
    caste_master_id: PositiveID | None = None


class ReligionMasterBase(SchemaBase):
    religion_name: NonEmptyStr | None = None


class ReligionMasterCreate(ReligionMasterBase):
    religion_id: PositiveID


class ReligionMasterUpdate(ReligionMasterBase):
    pass


class ReligionMasterResponse(ReligionMasterBase, ORMBase):
    religion_id: PositiveID


class ReligionMasterSummary(ORMBase):
    religion_id: PositiveID
    religion_name: str | None = None


class ReligionMasterSearch(SearchBase):
    religion_id: PositiveID | None = None


class ReligionMasterFilter(SchemaBase):
    religion_id: PositiveID | None = None


class OccupationMasterBase(SchemaBase):
    occupation_name: NonEmptyStr | None = None


class OccupationMasterCreate(OccupationMasterBase):
    occupation_id: PositiveID


class OccupationMasterUpdate(OccupationMasterBase):
    pass


class OccupationMasterResponse(OccupationMasterBase, ORMBase):
    occupation_id: PositiveID


class OccupationMasterSummary(ORMBase):
    occupation_id: PositiveID
    occupation_name: str | None = None


class OccupationMasterSearch(SearchBase):
    occupation_id: PositiveID | None = None


class OccupationMasterFilter(SchemaBase):
    occupation_id: PositiveID | None = None


class ActBase(SchemaBase):
    act_description: NonEmptyStr | None = None
    short_name: NonEmptyStr | None = None
    active: bool | None = None


class ActCreate(ActBase):
    act_code: NonEmptyStr


class ActUpdate(ActBase):
    pass


class ActResponse(ActBase, ORMBase):
    act_code: str


class ActSummary(ORMBase):
    act_code: str
    short_name: str | None = None
    act_description: str | None = None
    active: bool | None = None


class ActSearch(SearchBase, ActiveFilterBase):
    act_code: NonEmptyStr | None = None


class ActFilter(ActiveFilterBase):
    act_code: NonEmptyStr | None = None


class SectionBase(SchemaBase):
    act_code: NonEmptyStr | None = None
    section_description: NonEmptyStr | None = None
    active: bool | None = None


class SectionCreate(SectionBase):
    section_code: NonEmptyStr


class SectionUpdate(SectionBase):
    pass


class SectionResponse(SectionBase, ORMBase):
    section_code: str


class SectionSummary(ORMBase):
    section_code: str
    act_code: str | None = None
    section_description: str | None = None
    active: bool | None = None


class SectionSearch(SearchBase, ActiveFilterBase):
    section_code: NonEmptyStr | None = None
    act_code: NonEmptyStr | None = None


class SectionFilter(ActiveFilterBase):
    section_code: NonEmptyStr | None = None
    act_code: NonEmptyStr | None = None


class CaseMasterBase(SchemaBase):
    crime_no: CrimeNoStr | None = None
    case_no: CaseNoStr | None = None
    crime_registered_date: date | None = None
    police_person_id: PositiveID | None = None
    police_station_id: PositiveID | None = None
    case_category_id: PositiveID | None = None
    gravity_offence_id: PositiveID | None = None
    crime_major_head_id: PositiveID | None = None
    crime_minor_head_id: PositiveID | None = None
    case_status_id: PositiveID | None = None
    court_id: PositiveID | None = None
    incident_from_date: datetime | None = None
    incident_to_date: datetime | None = None
    info_received_ps_date: datetime | None = None
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    brief_facts: str | None = None

    @model_validator(mode="after")
    def validate_case_values(self) -> Self:
        if self.crime_no and self.case_no and not self.crime_no.endswith(self.case_no):
            raise ValueError("case_no must match the last 9 digits of crime_no")
        if (
            self.incident_from_date
            and self.incident_to_date
            and self.incident_to_date < self.incident_from_date
        ):
            raise ValueError(
                "incident_to_date must be greater than or equal to incident_from_date"
            )
        return self


class CaseMasterCreate(CaseMasterBase):
    case_master_id: PositiveID


class CaseMasterUpdate(CaseMasterBase):
    pass


class CaseMasterResponse(CaseMasterBase, ORMBase):
    case_master_id: PositiveID


class CaseMasterSummary(ORMBase):
    case_master_id: PositiveID
    crime_no: str | None = None
    case_no: str | None = None
    crime_registered_date: date | None = None
    police_station_id: int | None = None
    case_category_id: int | None = None
    case_status_id: int | None = None


class CaseMasterSearch(SearchBase):
    crime_no: CrimeNoStr | None = None
    case_no: CaseNoStr | None = None
    police_station_id: PositiveID | None = None
    case_category_id: PositiveID | None = None
    case_status_id: PositiveID | None = None
    registered_from: date | None = None
    registered_to: date | None = None

    @model_validator(mode="after")
    def validate_registered_range(self) -> Self:
        if self.registered_from and self.registered_to and self.registered_to < self.registered_from:
            raise ValueError(
                "registered_to must be greater than or equal to registered_from"
            )
        return self


class CaseMasterFilter(SchemaBase):
    case_master_id: PositiveID | None = None
    crime_no: CrimeNoStr | None = None
    case_no: CaseNoStr | None = None
    police_person_id: PositiveID | None = None
    police_station_id: PositiveID | None = None
    case_category_id: PositiveID | None = None
    gravity_offence_id: PositiveID | None = None
    crime_major_head_id: PositiveID | None = None
    crime_minor_head_id: PositiveID | None = None
    case_status_id: PositiveID | None = None
    court_id: PositiveID | None = None
    registered_from: date | None = None
    registered_to: date | None = None

    @model_validator(mode="after")
    def validate_registered_range(self) -> Self:
        if self.registered_from and self.registered_to and self.registered_to < self.registered_from:
            raise ValueError(
                "registered_to must be greater than or equal to registered_from"
            )
        return self


class InvOccuranceTimeBase(SchemaBase):
    case_master_id: PositiveID


class InvOccuranceTimeCreate(InvOccuranceTimeBase):
    pass


class InvOccuranceTimeUpdate(SchemaBase):
    pass


class InvOccuranceTimeResponse(InvOccuranceTimeBase, ORMBase):
    pass


class InvOccuranceTimeFilter(SchemaBase):
    case_master_id: PositiveID | None = None


class ComplainantDetailsBase(SchemaBase):
    case_master_id: PositiveID
    complainant_name: NonEmptyStr | None = None
    age_year: AgeYear | None = None
    occupation_id: PositiveID | None = None
    religion_id: PositiveID | None = None
    caste_id: PositiveID | None = None
    gender_id: PositiveID | None = None


class ComplainantDetailsCreate(ComplainantDetailsBase):
    complainant_id: PositiveID


class ComplainantDetailsUpdate(SchemaBase):
    complainant_name: NonEmptyStr | None = None
    age_year: AgeYear | None = None
    occupation_id: PositiveID | None = None
    religion_id: PositiveID | None = None
    caste_id: PositiveID | None = None
    gender_id: PositiveID | None = None


class ComplainantDetailsResponse(ComplainantDetailsBase, ORMBase):
    complainant_id: PositiveID


class ComplainantDetailsSummary(ORMBase):
    complainant_id: PositiveID
    case_master_id: int
    complainant_name: str | None = None
    age_year: int | None = None
    gender_id: int | None = None


class ComplainantDetailsSearch(SearchBase):
    case_master_id: PositiveID | None = None
    occupation_id: PositiveID | None = None
    religion_id: PositiveID | None = None
    caste_id: PositiveID | None = None
    gender_id: PositiveID | None = None


class ComplainantDetailsFilter(SchemaBase):
    complainant_id: PositiveID | None = None
    case_master_id: PositiveID | None = None
    occupation_id: PositiveID | None = None
    religion_id: PositiveID | None = None
    caste_id: PositiveID | None = None
    gender_id: PositiveID | None = None


class ActSectionAssociationBase(SchemaBase):
    case_master_id: PositiveID
    act_id: NonEmptyStr
    section_id: NonEmptyStr
    act_order_id: int | None = Field(default=None, ge=0)
    section_order_id: int | None = Field(default=None, ge=0)


class ActSectionAssociationCreate(ActSectionAssociationBase):
    pass


class ActSectionAssociationUpdate(SchemaBase):
    act_order_id: int | None = Field(default=None, ge=0)
    section_order_id: int | None = Field(default=None, ge=0)


class ActSectionAssociationResponse(ActSectionAssociationBase, ORMBase):
    pass


class ActSectionAssociationFilter(SchemaBase):
    case_master_id: PositiveID | None = None
    act_id: NonEmptyStr | None = None
    section_id: NonEmptyStr | None = None


class VictimBase(SchemaBase):
    case_master_id: PositiveID
    victim_name: NonEmptyStr | None = None
    age_year: AgeYear | None = None
    gender_id: PositiveID | None = None
    victim_police: Literal["0", "1"] | None = None


class VictimCreate(VictimBase):
    victim_master_id: PositiveID


class VictimUpdate(SchemaBase):
    victim_name: NonEmptyStr | None = None
    age_year: AgeYear | None = None
    gender_id: PositiveID | None = None
    victim_police: Literal["0", "1"] | None = None


class VictimResponse(VictimBase, ORMBase):
    victim_master_id: PositiveID


class VictimSummary(ORMBase):
    victim_master_id: PositiveID
    case_master_id: int
    victim_name: str | None = None
    age_year: int | None = None
    gender_id: int | None = None
    victim_police: str | None = None


class VictimSearch(SearchBase):
    case_master_id: PositiveID | None = None
    gender_id: PositiveID | None = None
    victim_police: Literal["0", "1"] | None = None


class VictimFilter(SchemaBase):
    victim_master_id: PositiveID | None = None
    case_master_id: PositiveID | None = None
    gender_id: PositiveID | None = None
    victim_police: Literal["0", "1"] | None = None


class AccusedBase(SchemaBase):
    case_master_id: PositiveID
    accused_name: NonEmptyStr | None = None
    age_year: AgeYear | None = None
    gender_id: PositiveID | None = None
    person_id: PersonOrderStr | None = None


class AccusedCreate(AccusedBase):
    accused_master_id: PositiveID


class AccusedUpdate(SchemaBase):
    accused_name: NonEmptyStr | None = None
    age_year: AgeYear | None = None
    gender_id: PositiveID | None = None
    person_id: PersonOrderStr | None = None


class AccusedResponse(AccusedBase, ORMBase):
    accused_master_id: PositiveID


class AccusedSummary(ORMBase):
    accused_master_id: PositiveID
    case_master_id: int
    accused_name: str | None = None
    age_year: int | None = None
    gender_id: int | None = None
    person_id: str | None = None


class AccusedSearch(SearchBase):
    case_master_id: PositiveID | None = None
    gender_id: PositiveID | None = None
    person_id: PersonOrderStr | None = None


class AccusedFilter(SchemaBase):
    accused_master_id: PositiveID | None = None
    case_master_id: PositiveID | None = None
    gender_id: PositiveID | None = None
    person_id: PersonOrderStr | None = None


class ArrestSurrenderBase(SchemaBase):
    case_master_id: PositiveID
    arrest_surrender_type_id: PositiveID | None = None
    arrest_surrender_date: date | None = None
    arrest_surrender_state_id: PositiveID | None = None
    arrest_surrender_district_id: PositiveID | None = None
    police_station_id: PositiveID | None = None
    io_id: PositiveID | None = None
    court_id: PositiveID | None = None
    accused_master_id: PositiveID | None = None
    is_accused: bool | None = None
    is_complainant_accused: bool | None = None


class ArrestSurrenderCreate(ArrestSurrenderBase):
    arrest_surrender_id: PositiveID


class ArrestSurrenderUpdate(SchemaBase):
    arrest_surrender_type_id: PositiveID | None = None
    arrest_surrender_date: date | None = None
    arrest_surrender_state_id: PositiveID | None = None
    arrest_surrender_district_id: PositiveID | None = None
    police_station_id: PositiveID | None = None
    io_id: PositiveID | None = None
    court_id: PositiveID | None = None
    accused_master_id: PositiveID | None = None
    is_accused: bool | None = None
    is_complainant_accused: bool | None = None


class ArrestSurrenderResponse(ArrestSurrenderBase, ORMBase):
    arrest_surrender_id: PositiveID


class ArrestSurrenderSummary(ORMBase):
    arrest_surrender_id: PositiveID
    case_master_id: int
    accused_master_id: int | None = None
    arrest_surrender_date: date | None = None
    police_station_id: int | None = None
    io_id: int | None = None


class ArrestSurrenderSearch(SearchBase):
    case_master_id: PositiveID | None = None
    accused_master_id: PositiveID | None = None
    police_station_id: PositiveID | None = None
    io_id: PositiveID | None = None
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


class ArrestSurrenderFilter(SchemaBase):
    arrest_surrender_id: PositiveID | None = None
    case_master_id: PositiveID | None = None
    arrest_surrender_type_id: PositiveID | None = None
    arrest_surrender_state_id: PositiveID | None = None
    arrest_surrender_district_id: PositiveID | None = None
    police_station_id: PositiveID | None = None
    io_id: PositiveID | None = None
    court_id: PositiveID | None = None
    accused_master_id: PositiveID | None = None
    is_accused: bool | None = None
    is_complainant_accused: bool | None = None
    date_from: date | None = None
    date_to: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


class InvArrestSurrenderAccusedBase(SchemaBase):
    arrest_surrender_id: PositiveID
    accused_master_id: PositiveID


class InvArrestSurrenderAccusedCreate(InvArrestSurrenderAccusedBase):
    pass


class InvArrestSurrenderAccusedUpdate(SchemaBase):
    pass


class InvArrestSurrenderAccusedResponse(InvArrestSurrenderAccusedBase, ORMBase):
    pass


class InvArrestSurrenderAccusedFilter(SchemaBase):
    arrest_surrender_id: PositiveID | None = None
    accused_master_id: PositiveID | None = None


class CrimeHeadActSectionBase(SchemaBase):
    crime_head_id: PositiveID
    act_code: NonEmptyStr
    section_code: NonEmptyStr


class CrimeHeadActSectionCreate(CrimeHeadActSectionBase):
    pass


class CrimeHeadActSectionUpdate(SchemaBase):
    pass


class CrimeHeadActSectionResponse(CrimeHeadActSectionBase, ORMBase):
    pass


class CrimeHeadActSectionFilter(SchemaBase):
    crime_head_id: PositiveID | None = None
    act_code: NonEmptyStr | None = None
    section_code: NonEmptyStr | None = None


class ChargesheetDetailsBase(SchemaBase):
    case_master_id: PositiveID
    cs_date: datetime | None = None
    cs_type: Literal["A", "B", "C"] | None = None
    police_person_id: PositiveID | None = None


class ChargesheetDetailsCreate(ChargesheetDetailsBase):
    cs_id: PositiveID


class ChargesheetDetailsUpdate(SchemaBase):
    cs_date: datetime | None = None
    cs_type: Literal["A", "B", "C"] | None = None
    police_person_id: PositiveID | None = None


class ChargesheetDetailsResponse(ChargesheetDetailsBase, ORMBase):
    cs_id: PositiveID


class ChargesheetDetailsSummary(ORMBase):
    cs_id: PositiveID
    case_master_id: int
    cs_date: datetime | None = None
    cs_type: str | None = None
    police_person_id: int | None = None


class ChargesheetDetailsSearch(SearchBase):
    case_master_id: PositiveID | None = None
    cs_type: Literal["A", "B", "C"] | None = None
    police_person_id: PositiveID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


class ChargesheetDetailsFilter(SchemaBase):
    cs_id: PositiveID | None = None
    case_master_id: PositiveID | None = None
    cs_type: Literal["A", "B", "C"] | None = None
    police_person_id: PositiveID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if self.date_from and self.date_to and self.date_to < self.date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return self


__all__ = [
    "AccusedCreate",
    "AccusedFilter",
    "AccusedResponse",
    "AccusedSearch",
    "AccusedSummary",
    "AccusedUpdate",
    "ActCreate",
    "ActFilter",
    "ActResponse",
    "ActSearch",
    "ActSectionAssociationCreate",
    "ActSectionAssociationFilter",
    "ActSectionAssociationResponse",
    "ActSectionAssociationUpdate",
    "ActSummary",
    "ActUpdate",
    "ArrestSurrenderCreate",
    "ArrestSurrenderFilter",
    "ArrestSurrenderResponse",
    "ArrestSurrenderSearch",
    "ArrestSurrenderSummary",
    "ArrestSurrenderUpdate",
    "CaseCategoryCreate",
    "CaseCategoryFilter",
    "CaseCategoryResponse",
    "CaseCategorySearch",
    "CaseCategorySummary",
    "CaseCategoryUpdate",
    "CaseMasterCreate",
    "CaseMasterFilter",
    "CaseMasterResponse",
    "CaseMasterSearch",
    "CaseMasterSummary",
    "CaseMasterUpdate",
    "CaseStatusMasterCreate",
    "CaseStatusMasterFilter",
    "CaseStatusMasterResponse",
    "CaseStatusMasterSearch",
    "CaseStatusMasterSummary",
    "CaseStatusMasterUpdate",
    "CasteMasterCreate",
    "CasteMasterFilter",
    "CasteMasterResponse",
    "CasteMasterSearch",
    "CasteMasterSummary",
    "CasteMasterUpdate",
    "ChargesheetDetailsCreate",
    "ChargesheetDetailsFilter",
    "ChargesheetDetailsResponse",
    "ChargesheetDetailsSearch",
    "ChargesheetDetailsSummary",
    "ChargesheetDetailsUpdate",
    "ComplainantDetailsCreate",
    "ComplainantDetailsFilter",
    "ComplainantDetailsResponse",
    "ComplainantDetailsSearch",
    "ComplainantDetailsSummary",
    "ComplainantDetailsUpdate",
    "CourtCreate",
    "CourtFilter",
    "CourtResponse",
    "CourtSearch",
    "CourtSummary",
    "CourtUpdate",
    "CrimeHeadActSectionCreate",
    "CrimeHeadActSectionFilter",
    "CrimeHeadActSectionResponse",
    "CrimeHeadActSectionUpdate",
    "CrimeHeadCreate",
    "CrimeHeadFilter",
    "CrimeHeadResponse",
    "CrimeHeadSearch",
    "CrimeHeadSummary",
    "CrimeHeadUpdate",
    "CrimeSubHeadCreate",
    "CrimeSubHeadFilter",
    "CrimeSubHeadResponse",
    "CrimeSubHeadSearch",
    "CrimeSubHeadSummary",
    "CrimeSubHeadUpdate",
    "DesignationCreate",
    "DesignationFilter",
    "DesignationResponse",
    "DesignationSearch",
    "DesignationSummary",
    "DesignationUpdate",
    "DistrictCreate",
    "DistrictFilter",
    "DistrictResponse",
    "DistrictSearch",
    "DistrictSummary",
    "DistrictUpdate",
    "EmployeeCreate",
    "EmployeeFilter",
    "EmployeeResponse",
    "EmployeeSearch",
    "EmployeeSummary",
    "EmployeeUpdate",
    "GravityOffenceCreate",
    "GravityOffenceFilter",
    "GravityOffenceResponse",
    "GravityOffenceSearch",
    "GravityOffenceSummary",
    "GravityOffenceUpdate",
    "InvArrestSurrenderAccusedCreate",
    "InvArrestSurrenderAccusedFilter",
    "InvArrestSurrenderAccusedResponse",
    "InvArrestSurrenderAccusedUpdate",
    "InvOccuranceTimeCreate",
    "InvOccuranceTimeFilter",
    "InvOccuranceTimeResponse",
    "InvOccuranceTimeUpdate",
    "OccupationMasterCreate",
    "OccupationMasterFilter",
    "OccupationMasterResponse",
    "OccupationMasterSearch",
    "OccupationMasterSummary",
    "OccupationMasterUpdate",
    "RankCreate",
    "RankFilter",
    "RankResponse",
    "RankSearch",
    "RankSummary",
    "RankUpdate",
    "ReligionMasterCreate",
    "ReligionMasterFilter",
    "ReligionMasterResponse",
    "ReligionMasterSearch",
    "ReligionMasterSummary",
    "ReligionMasterUpdate",
    "SectionCreate",
    "SectionFilter",
    "SectionResponse",
    "SectionSearch",
    "SectionSummary",
    "SectionUpdate",
    "StateCreate",
    "StateFilter",
    "StateResponse",
    "StateSearch",
    "StateSummary",
    "StateUpdate",
    "UnitCreate",
    "UnitFilter",
    "UnitResponse",
    "UnitSearch",
    "UnitSummary",
    "UnitTypeCreate",
    "UnitTypeFilter",
    "UnitTypeResponse",
    "UnitTypeSearch",
    "UnitTypeSummary",
    "UnitTypeUpdate",
    "UnitUpdate",
    "VictimCreate",
    "VictimFilter",
    "VictimResponse",
    "VictimSearch",
    "VictimSummary",
    "VictimUpdate",
]
