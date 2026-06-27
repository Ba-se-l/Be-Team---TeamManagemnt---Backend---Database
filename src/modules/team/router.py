"""Team domain router.

Provides HTTP endpoints for managing teams. All endpoints
require a valid JWT token. Authorization logic (ADMIN/SUPER_ADMIN roles)
is enforced in the service layer.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID
from typing import Annotated

from src.database import get_session
from src.modules.auth.dependencies import get_current_user
from src.modules.user import User
from .schemas import CreateTeamRequest, UpdateTeamRequest, TeamResponse
from . import service

router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
)
async def create_team(
    request: CreateTeamRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TeamResponse:
    """Creates a new team and assigns the creator as SUPER_ADMIN."""
    team = await service.create_team(
        schema=request,
        current_user=current_user,
        session=session,
    )
    return TeamResponse.model_validate(team)


@router.get(
    "/",
    response_model=list[TeamResponse],
    status_code=status.HTTP_200_OK,
    summary="List user's teams",
)
async def list_user_teams(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[TeamResponse]:
    """Lists all teams that the currently authenticated user is a member of."""
    teams = await service.list_user_teams(
        user_id=current_user.id,
        session=session,
        skip=skip,
        limit=limit,
    )
    return [TeamResponse.model_validate(t) for t in teams]


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Get team by ID",
)
async def get_team(
    team_id: ID,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> TeamResponse:
    """Fetches a specific team by its UUID."""
    team = await service._get_team(team_id=team_id, session=session)
    return TeamResponse.model_validate(team)


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a team",
)
async def update_team(
    team_id: ID,
    request: UpdateTeamRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TeamResponse:
    """Updates team details. Requires ADMIN or SUPER_ADMIN role in the team."""
    team = await service.update_team(
        team_id=team_id,
        schema=request,
        current_user=current_user,
        session=session,
    )
    return TeamResponse.model_validate(team)


@router.delete(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a team",
)
async def delete_team(
    team_id: ID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TeamResponse:
    """Soft-deletes a team. Requires SUPER_ADMIN role in the team."""
    team = await service.soft_delete_team(
        team_id=team_id,
        current_user=current_user,
        session=session,
    )
    return TeamResponse.model_validate(team)
