"""Task domain router.

Provides HTTP endpoints for managing tasks.
Creation and listing are nested under the project route.
Fetching, updating, and deleting are top-level task routes.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID
from typing import Annotated

from src.database import get_session
from src.modules.auth.dependencies import get_current_user
from src.modules.user import User
from .schemas import CreateTaskRequest, UpdateTasksRequest, TaskResponse
from . import service

project_nested_router = APIRouter(prefix="/api/v1/projects/{project_id}/tasks", tags=["Tasks"])
top_level_router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@project_nested_router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task in a project",
)
async def create_task(
    project_id: ID,
    request: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Creates a new task within a project. Creator must be a team member."""
    task = await service.create_task(
        project_id=project_id,
        schema=request,
        creator=current_user,
        session=session,
    )
    
    return TaskResponse.model_validate(task)


@project_nested_router.get(
    "/",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List project tasks",
)
async def list_project_tasks(
    project_id: ID,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> list[TaskResponse]:
    """Retrieves a paginated list of all active tasks in a project."""
    tasks = await service.list_project_tasks(
        project_id=project_id,
        session=session,
        skip=skip,
        limit=limit,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@top_level_router.get(
    "/me",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks assigned to me",
)
async def list_my_tasks(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[TaskResponse]:
    """Retrieves a paginated list of all tasks assigned to the current user."""
    tasks = await service.list_user_assigned_tasks(
        user_id=current_user.id,
        session=session,
        skip=skip,
        limit=limit,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@top_level_router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
)
async def get_task(
    task_id: ID,
    current_user: User = Depends(get_current_user),  # Enforce auth
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Fetches a specific task by its UUID."""
    task = await service._get_task(task_id=task_id, session=session)
    return TaskResponse.model_validate(task)


@top_level_router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
)
async def update_task(
    task_id: ID,
    request: UpdateTasksRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Updates a task. Updater must be a member of the owning team."""
    task = await service.update_task(
        task_id=task_id,
        schema=request,
        current_user=current_user,
        session=session,
    )
    return TaskResponse.model_validate(task)


@top_level_router.delete(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a task",
)
async def delete_task(
    task_id: ID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Soft-deletes a task. Deleter must be a member of the owning team."""
    task = await service.soft_delete_task(
        task_id=task_id,
        current_user=current_user,
        session=session,
    )
    return TaskResponse.model_validate(task)
