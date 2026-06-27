"""Team Members domain router.

Provides HTTP endpoints for managing team memberships.
These endpoints are nested under the ``/teams/{team_id}/members`` path.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID
from typing import Annotated

from src.database import get_session
from src.modules.auth.dependencies import get_current_user
from src.modules.user import User
from .schemas import AddMemberRequest, UpdateMemberRoleRequest, MemberResponse
from . import service

router = APIRouter(prefix="/api/v1/teams/{team_id}/members", tags=["Team Members"])


@router.post(
    "/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to the team",
)
async def add_member(
    team_id: ID,
    request: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MemberResponse:
    """Adds a new member to the team. Requires ADMIN+ role."""
    membership = await service.add_member(
        team_id=team_id,
        schema=request,
        adder=current_user,
        session=session,
    )
    return MemberResponse.model_validate(membership)


@router.get(
    "/",
    response_model=list[MemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List team members",
)
async def list_members(
    team_id: ID,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> list[MemberResponse]:
    """Retrieves a paginated list of all members in the specified team."""
    members = await service.list_team_members(
        team_id=team_id,
        session=session,
        skip=skip,
        limit=limit,
    )
    return [MemberResponse.model_validate(m) for m in members]


@router.patch(
    "/{user_id}",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a member's role",
)
async def update_member_role(
    team_id: ID,
    user_id: ID,
    request: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MemberResponse:
    """Updates the role of a team member. Requires SUPER_ADMIN role."""
    membership = await service.update_member_role(
        team_id=team_id,
        user_id=user_id,
        schema=request,
        updater=current_user,
        session=session,
    )
    return MemberResponse.model_validate(membership)


@router.delete(
    "/{user_id}",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove a member from the team",
)
async def remove_member(
    team_id: ID,
    user_id: ID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> MemberResponse:
    """Removes a member from the team. Requires ADMIN+ role."""
    membership = await service.remove_member(
        team_id=team_id,
        user_id=user_id,
        remover=current_user,
        session=session,
    )
    return MemberResponse.model_validate(membership)
