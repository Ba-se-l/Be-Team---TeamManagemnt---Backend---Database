"""Technology domain router.

Provides HTTP endpoints for managing the global technology catalog.
Since this is a global dictionary table, endpoints do not strictly
require team RBAC checks for MVP, but they do require authentication.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID
from typing import Annotated

from src.database import get_session
from src.modules.auth.dependencies import get_current_user
from src.modules.user import User
from .schemas import CreateTechnologyRequest, UpdateTechnologyRequest, TechnologyResponse
from . import service

router = APIRouter(prefix="/api/v1/technologies", tags=["Technologies"])


@router.post(
    "/",
    response_model=TechnologyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a technology",
)
async def create_technology(
    request: CreateTechnologyRequest,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> TechnologyResponse:
    """Creates a new technology entry in the global catalog."""
    tech = await service.create_technology(schema=request, session=session)
    return TechnologyResponse.model_validate(tech)


@router.get(
    "/search",
    response_model=list[TechnologyResponse],
    status_code=status.HTTP_200_OK,
    summary="Search technologies",
)
async def search_technologies(
    q: Annotated[str, Query(min_length=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> list[TechnologyResponse]:
    """Searches the technology catalog by partial name match (case-insensitive)."""
    techs = await service.search_technologies(
        query=q,
        session=session,
        skip=skip,
        limit=limit,
    )
    return [TechnologyResponse.model_validate(t) for t in techs]


@router.get(
    "/",
    response_model=list[TechnologyResponse],
    status_code=status.HTTP_200_OK,
    summary="List all technologies",
)
async def list_technologies(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> list[TechnologyResponse]:
    """Retrieves a paginated list of all technologies in the catalog."""
    techs = await service.list_technologies(
        session=session,
        skip=skip,
        limit=limit,
    )
    return [TechnologyResponse.model_validate(t) for t in techs]


@router.get(
    "/{tech_id}",
    response_model=TechnologyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get technology by ID",
)
async def get_technology(
    tech_id: ID,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> TechnologyResponse:
    """Fetches a specific technology by its UUID."""
    tech = await service._get_technology(tech_id=tech_id, session=session)
    return TechnologyResponse.model_validate(tech)


@router.patch(
    "/{tech_id}",
    response_model=TechnologyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a technology",
)
async def update_technology(
    tech_id: ID,
    request: UpdateTechnologyRequest,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> TechnologyResponse:
    """Updates an existing technology entry."""
    tech = await service.update_technology(
        tech_id=tech_id,
        schema=request,
        session=session,
    )
    return TechnologyResponse.model_validate(tech)


@router.delete(
    "/{tech_id}",
    response_model=TechnologyResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a technology",
)
async def delete_technology(
    tech_id: ID,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> TechnologyResponse:
    """Hard-deletes a technology from the catalog."""
    tech = await service.delete_technology(tech_id=tech_id, session=session)
    return TechnologyResponse.model_validate(tech)
