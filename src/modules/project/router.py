"""Project domain router.

Provides HTTP endpoints for managing projects.
Creation and listing are nested under the team route.
Fetching, updating, and deleting are top-level project routes.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID
from typing import Annotated

from src.database import get_session
from src.modules.auth.dependencies import get_current_user
from src.modules.user import User
from .schemas import CreateProjectRequest, UpdateProjectRequest, ProjectResponse
from . import service

# We use two routers here: one nested under teams, one top-level.
team_nested_router = APIRouter(prefix="/api/v1/teams/{team_id}/projects", tags=["Projects"])
top_level_router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@team_nested_router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project in a team",
)
async def create_project(
    team_id: ID,
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    """Creates a new project within a team. Requires ADMIN+ role in the team."""
    project = await service.create_project(
        team_id=team_id,
        schema=request,
        creator=current_user,
        session=session,
    )
    
    return ProjectResponse.model_validate(project)


@team_nested_router.get(
    "/",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List team projects",
)
async def list_team_projects(
    team_id: ID,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> list[ProjectResponse]:
    """Retrieves a paginated list of all active projects in a team."""
    projects = await service.list_team_projects(
        team_id=team_id,
        session=session,
        skip=skip,
        limit=limit,
    )
    return [ProjectResponse.model_validate(p) for p in projects]


@top_level_router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project by ID",
)
async def get_project(
    project_id: ID,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    """Fetches a specific project by its UUID."""
    project = await service._get_project(project_id=project_id, session=session)
    return ProjectResponse.model_validate(project)


@top_level_router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a project",
)
async def update_project(
    project_id: ID,
    request: UpdateProjectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    """Updates a project. Requires ADMIN+ role in the owning team."""
    project = await service.update_project(
        project_id=project_id,
        schema=request,
        current_user=current_user,
        session=session,
    )
    return ProjectResponse.model_validate(project)


@top_level_router.delete(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a project",
)
async def delete_project(
    project_id: ID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    """Soft-deletes a project. Requires SUPER_ADMIN role in the owning team."""
    project = await service.soft_delete_project(
        project_id=project_id,
        current_user=current_user,
        session=session,
    )
    return ProjectResponse.model_validate(project)
