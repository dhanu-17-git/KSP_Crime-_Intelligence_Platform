"""Production-ready CRUD routers for all KSP domain entities.

GET endpoints are public (no auth required) for hackathon demo.
POST/PATCH/DELETE require JWT authentication with appropriate roles.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import Role
from app.database import get_db_session
from app.dependencies.auth import require_roles
from app.schemas.response import ApiResponse
from app.services.base_service import BaseService
from app.utils.responses import success_response

# ── Auth dependency — write operations require OFFICER+ ─────────────────────

write_access = Depends(require_roles([Role.SUPER_ADMIN, Role.ADMIN, Role.INVESTIGATOR, Role.OFFICER]))


# ── Router factory ──────────────────────────────────────────────────────────

def _build_crud_router(
    *,
    prefix: str,
    tag: str,
    service_class: type[BaseService],  # type: ignore[type-arg]
    pk_name: str,
    pk_type: type = int,
    response_schema: type,
    create_schema: type,
    update_schema: type,
) -> APIRouter:
    """Generate a complete CRUD router for a given entity service."""

    router = APIRouter(prefix=prefix, tags=[tag])

    # --- LIST (paginated, searchable, filterable) ---
    @router.get(
        "",
        response_model=ApiResponse[list[response_schema]],  # type: ignore[valid-type]
        status_code=status.HTTP_200_OK,
    )
    async def list_items(
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=500),
        search: str | None = Query(None),
        sort_by: str | None = Query(None),
        sort_desc: bool = Query(False),
        session: AsyncSession = Depends(get_db_session),
    ) -> ApiResponse:
        svc = service_class(session)
        result = await svc.paginate(
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )
        return success_response(
            request=request,
            message=f"Retrieved {len(result.items)} of {result.total} records",
            data=[response_schema.model_validate(item) for item in result.items],
        )

    # --- GET by ID ---
    @router.get(
        "/{pk}",
        response_model=ApiResponse[response_schema],  # type: ignore[valid-type]
        status_code=status.HTTP_200_OK,
    )
    async def get_item(
        request: Request,
        pk: pk_type,  # type: ignore[valid-type]
        session: AsyncSession = Depends(get_db_session),
    ) -> ApiResponse:
        svc = service_class(session)
        instance = await svc.get_or_404(pk)
        return success_response(
            request=request,
            message="Record retrieved",
            data=response_schema.model_validate(instance),
        )

    # --- CREATE ---
    @router.post(
        "",
        response_model=ApiResponse[response_schema],  # type: ignore[valid-type]
        status_code=status.HTTP_201_CREATED,
    )
    async def create_item(
        request: Request,
        body: create_schema,  # type: ignore[valid-type]
        session: AsyncSession = Depends(get_db_session),
        _auth: Any = write_access,
    ) -> ApiResponse:
        svc = service_class(session)
        instance = await svc.create(body.model_dump(exclude_unset=True))
        return success_response(
            request=request,
            message="Record created",
            data=response_schema.model_validate(instance),
        )

    # --- PATCH ---
    @router.patch(
        "/{pk}",
        response_model=ApiResponse[response_schema],  # type: ignore[valid-type]
        status_code=status.HTTP_200_OK,
    )
    async def update_item(
        request: Request,
        pk: pk_type,  # type: ignore[valid-type]
        body: update_schema,  # type: ignore[valid-type]
        session: AsyncSession = Depends(get_db_session),
        _auth: Any = write_access,
    ) -> ApiResponse:
        svc = service_class(session)
        instance = await svc.update(pk, body.model_dump(exclude_unset=True))
        return success_response(
            request=request,
            message="Record updated",
            data=response_schema.model_validate(instance),
        )

    # --- DELETE ---
    @router.delete(
        "/{pk}",
        response_model=ApiResponse[None],
        status_code=status.HTTP_200_OK,
    )
    async def delete_item(
        request: Request,
        pk: pk_type,  # type: ignore[valid-type]
        session: AsyncSession = Depends(get_db_session),
        _auth: Any = write_access,
    ) -> ApiResponse:
        svc = service_class(session)
        await svc.delete(pk)
        return success_response(request=request, message="Record deleted")

    return router


# ── Import schemas ──────────────────────────────────────────────────────────

from app.schemas.fir import (  # noqa: E402
    AccusedCreate,
    AccusedResponse,
    AccusedUpdate,
    ActCreate,
    ActResponse,
    ActUpdate,
    ArrestSurrenderCreate,
    ArrestSurrenderResponse,
    ArrestSurrenderUpdate,
    CaseCategoryCreate,
    CaseCategoryResponse,
    CaseCategoryUpdate,
    CaseMasterCreate,
    CaseMasterResponse,
    CaseMasterUpdate,
    CaseStatusMasterCreate,
    CaseStatusMasterResponse,
    CaseStatusMasterUpdate,
    CasteMasterCreate,
    CasteMasterResponse,
    CasteMasterUpdate,
    ChargesheetDetailsCreate,
    ChargesheetDetailsResponse,
    ChargesheetDetailsUpdate,
    ComplainantDetailsCreate,
    ComplainantDetailsResponse,
    ComplainantDetailsUpdate,
    CourtCreate,
    CourtResponse,
    CourtUpdate,
    CrimeHeadCreate,
    CrimeHeadResponse,
    CrimeHeadUpdate,
    CrimeSubHeadCreate,
    CrimeSubHeadResponse,
    CrimeSubHeadUpdate,
    DesignationCreate,
    DesignationResponse,
    DesignationUpdate,
    DistrictCreate,
    DistrictResponse,
    DistrictUpdate,
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
    GravityOffenceCreate,
    GravityOffenceResponse,
    GravityOffenceUpdate,
    OccupationMasterCreate,
    OccupationMasterResponse,
    OccupationMasterUpdate,
    RankCreate,
    RankResponse,
    RankUpdate,
    ReligionMasterCreate,
    ReligionMasterResponse,
    ReligionMasterUpdate,
    SectionCreate,
    SectionResponse,
    SectionUpdate,
    StateCreate,
    StateResponse,
    StateUpdate,
    UnitCreate,
    UnitResponse,
    UnitTypeCreate,
    UnitTypeResponse,
    UnitTypeUpdate,
    UnitUpdate,
    VictimCreate,
    VictimResponse,
    VictimUpdate,
)
from app.services import (  # noqa: E402
    AccusedService,
    ActService,
    ArrestSurrenderService,
    CaseCategoryService,
    CaseMasterService,
    CaseStatusMasterService,
    CasteMasterService,
    ChargesheetDetailsService,
    ComplainantDetailsService,
    CourtService,
    CrimeHeadService,
    CrimeSubHeadService,
    DesignationService,
    DistrictService,
    EmployeeService,
    GravityOffenceService,
    OccupationMasterService,
    RankService,
    ReligionMasterService,
    SectionService,
    StateService,
    UnitService,
    UnitTypeService,
    VictimService,
)

# ── Build routers ───────────────────────────────────────────────────────────

states_router = _build_crud_router(
    prefix="/states", tag="States",
    service_class=StateService, pk_name="state_id",
    response_schema=StateResponse, create_schema=StateCreate, update_schema=StateUpdate,
)

districts_router = _build_crud_router(
    prefix="/districts", tag="Districts",
    service_class=DistrictService, pk_name="district_id",
    response_schema=DistrictResponse, create_schema=DistrictCreate, update_schema=DistrictUpdate,
)

courts_router = _build_crud_router(
    prefix="/courts", tag="Courts",
    service_class=CourtService, pk_name="court_id",
    response_schema=CourtResponse, create_schema=CourtCreate, update_schema=CourtUpdate,
)

unit_types_router = _build_crud_router(
    prefix="/unit-types", tag="Unit Types",
    service_class=UnitTypeService, pk_name="unit_type_id",
    response_schema=UnitTypeResponse, create_schema=UnitTypeCreate, update_schema=UnitTypeUpdate,
)

units_router = _build_crud_router(
    prefix="/units", tag="Units",
    service_class=UnitService, pk_name="unit_id",
    response_schema=UnitResponse, create_schema=UnitCreate, update_schema=UnitUpdate,
)

ranks_router = _build_crud_router(
    prefix="/ranks", tag="Ranks",
    service_class=RankService, pk_name="rank_id",
    response_schema=RankResponse, create_schema=RankCreate, update_schema=RankUpdate,
)

designations_router = _build_crud_router(
    prefix="/designations", tag="Designations",
    service_class=DesignationService, pk_name="designation_id",
    response_schema=DesignationResponse, create_schema=DesignationCreate, update_schema=DesignationUpdate,
)

employees_router = _build_crud_router(
    prefix="/employees", tag="Employees",
    service_class=EmployeeService, pk_name="employee_id",
    response_schema=EmployeeResponse, create_schema=EmployeeCreate, update_schema=EmployeeUpdate,
)

case_categories_router = _build_crud_router(
    prefix="/case-categories", tag="Case Categories",
    service_class=CaseCategoryService, pk_name="case_category_id",
    response_schema=CaseCategoryResponse, create_schema=CaseCategoryCreate, update_schema=CaseCategoryUpdate,
)

gravity_offences_router = _build_crud_router(
    prefix="/gravity-offences", tag="Gravity Offences",
    service_class=GravityOffenceService, pk_name="gravity_offence_id",
    response_schema=GravityOffenceResponse, create_schema=GravityOffenceCreate, update_schema=GravityOffenceUpdate,
)

crime_heads_router = _build_crud_router(
    prefix="/crime-heads", tag="Crime Heads",
    service_class=CrimeHeadService, pk_name="crime_head_id",
    response_schema=CrimeHeadResponse, create_schema=CrimeHeadCreate, update_schema=CrimeHeadUpdate,
)

crime_sub_heads_router = _build_crud_router(
    prefix="/crime-sub-heads", tag="Crime Sub Heads",
    service_class=CrimeSubHeadService, pk_name="crime_sub_head_id",
    response_schema=CrimeSubHeadResponse, create_schema=CrimeSubHeadCreate, update_schema=CrimeSubHeadUpdate,
)

case_statuses_router = _build_crud_router(
    prefix="/case-statuses", tag="Case Statuses",
    service_class=CaseStatusMasterService, pk_name="case_status_id",
    response_schema=CaseStatusMasterResponse, create_schema=CaseStatusMasterCreate, update_schema=CaseStatusMasterUpdate,
)

castes_router = _build_crud_router(
    prefix="/castes", tag="Castes",
    service_class=CasteMasterService, pk_name="caste_master_id",
    response_schema=CasteMasterResponse, create_schema=CasteMasterCreate, update_schema=CasteMasterUpdate,
)

religions_router = _build_crud_router(
    prefix="/religions", tag="Religions",
    service_class=ReligionMasterService, pk_name="religion_id",
    response_schema=ReligionMasterResponse, create_schema=ReligionMasterCreate, update_schema=ReligionMasterUpdate,
)

occupations_router = _build_crud_router(
    prefix="/occupations", tag="Occupations",
    service_class=OccupationMasterService, pk_name="occupation_id",
    response_schema=OccupationMasterResponse, create_schema=OccupationMasterCreate, update_schema=OccupationMasterUpdate,
)

acts_router = _build_crud_router(
    prefix="/acts", tag="Acts",
    service_class=ActService, pk_name="act_code", pk_type=str,
    response_schema=ActResponse, create_schema=ActCreate, update_schema=ActUpdate,
)

sections_router = _build_crud_router(
    prefix="/sections", tag="Sections",
    service_class=SectionService, pk_name="section_code", pk_type=str,
    response_schema=SectionResponse, create_schema=SectionCreate, update_schema=SectionUpdate,
)

cases_router = _build_crud_router(
    prefix="/cases", tag="Cases",
    service_class=CaseMasterService, pk_name="case_master_id",
    response_schema=CaseMasterResponse, create_schema=CaseMasterCreate, update_schema=CaseMasterUpdate,
)

complainants_router = _build_crud_router(
    prefix="/complainants", tag="Complainants",
    service_class=ComplainantDetailsService, pk_name="complainant_id",
    response_schema=ComplainantDetailsResponse, create_schema=ComplainantDetailsCreate, update_schema=ComplainantDetailsUpdate,
)

victims_router = _build_crud_router(
    prefix="/victims", tag="Victims",
    service_class=VictimService, pk_name="victim_master_id",
    response_schema=VictimResponse, create_schema=VictimCreate, update_schema=VictimUpdate,
)

accused_router = _build_crud_router(
    prefix="/accused", tag="Accused",
    service_class=AccusedService, pk_name="accused_master_id",
    response_schema=AccusedResponse, create_schema=AccusedCreate, update_schema=AccusedUpdate,
)

arrests_router = _build_crud_router(
    prefix="/arrests", tag="Arrests",
    service_class=ArrestSurrenderService, pk_name="arrest_surrender_id",
    response_schema=ArrestSurrenderResponse, create_schema=ArrestSurrenderCreate, update_schema=ArrestSurrenderUpdate,
)

chargesheets_router = _build_crud_router(
    prefix="/chargesheets", tag="Chargesheets",
    service_class=ChargesheetDetailsService, pk_name="cs_id",
    response_schema=ChargesheetDetailsResponse, create_schema=ChargesheetDetailsCreate, update_schema=ChargesheetDetailsUpdate,
)


# ── Aggregate router for inclusion in main app ──────────────────────────────

v1_router = APIRouter()

_all_routers = [
    states_router,
    districts_router,
    courts_router,
    unit_types_router,
    units_router,
    ranks_router,
    designations_router,
    employees_router,
    case_categories_router,
    gravity_offences_router,
    crime_heads_router,
    crime_sub_heads_router,
    case_statuses_router,
    castes_router,
    religions_router,
    occupations_router,
    acts_router,
    sections_router,
    cases_router,
    complainants_router,
    victims_router,
    accused_router,
    arrests_router,
    chargesheets_router,
]

for _r in _all_routers:
    v1_router.include_router(_r)
