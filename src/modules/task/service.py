"""Task domain service layer.

Contains business logic for managing tasks within projects,
including creation, assignment, status updates, and listing.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID

from src.database import TaskStatus, UserRoles
from src.modules.user import User
from src.modules.team_members import TeamMemberRepository, InsufficientRoleException
from src.modules.project import ProjectRepository, ProjectNotFoundException
from .models import Task
from .schemas import CreateTaskRequest, UpdateTasksRequest
from .repository import TaskRepository
from .exceptions import TaskNotFoundException


async def _get_task(task_id: ID, session: AsyncSession) -> Task:
    """Internal helper: fetches a task by ID or raises.

    Args:
        task_id: The UUID of the task to fetch.
        session: The active database session.

    Returns:
        The ``Task`` ORM instance.

    Raises:
        TaskNotFoundException: If no task with the given ID exists.
    """
    repo = TaskRepository(session=session)
    task = await repo.get_by_id(id=task_id)

    if task is None:
        raise TaskNotFoundException(identifier=str(task_id))

    return task


async def create_task(
    project_id: ID,
    schema: CreateTaskRequest,
    creator: User,
    session: AsyncSession,
) -> Task:
    """Creates a new task within a project.

    Orchestration steps:
        1. Fetch the project to ensure it exists and get its team ID.
        2. Verify the creator is a member of the project's team.
        3. If ``assignee_to_id`` is provided, verify they are also a member.
        4. Build and persist the ``Task`` ORM instance.

    Args:
        project_id: The UUID of the project.
        schema: The validated task creation request.
        creator: The authenticated user creating the task.
        session: The active database session.

    Returns:
        The newly created ``Task`` ORM instance.

    Raises:
        ProjectNotFoundException: If the project does not exist.
        ValueError: If creator or assignee is not a team member.
    """
    task_repo = TaskRepository(session=session)
    project_repo = ProjectRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch project
    project = await project_repo.get_by_id(id=project_id)
    if project is None or not project.is_active:
        raise ProjectNotFoundException(identifier=str(project_id))

    if project.team_id is None:
        raise ValueError("Project is not attached to any team.")

    # Step 2: Verify creator is a member
    is_creator_member = await member_repo.check_if_membership(
        member_id=creator.id,
        team_id=project.team_id,
    )
    if not is_creator_member:
        raise ValueError("Creator must be a member of the project's team.")

    # Step 3: Verify assignee is a member (if provided)
    if schema.assignee_to_id:
        is_assignee_member = await member_repo.check_if_membership(
            member_id=schema.assignee_to_id,
            team_id=project.team_id,
        )
        if not is_assignee_member:
            raise ValueError("Assignee must be a member of the project's team.")

    # Step 4: Build and persist the ORM model
    task = Task(
        title=schema.title,
        description=schema.description,
        priority=schema.priority,
        deadline=schema.deadline,
        status=TaskStatus.TODO,
        project_id=project_id,
        creator_id=creator.id,
        assignee_to_id=schema.assignee_to_id,
    )

    task = await task_repo.create(orm_model=task)

    await session.flush()
    
    return task


async def update_task(
    task_id: ID,
    schema: UpdateTasksRequest,
    current_user: User,
    session: AsyncSession,
) -> Task:
    """Updates a task's details or status.

    Any team member can update tasks.

    Orchestration steps:
        1. Fetch the task.
        2. Fetch the project to get its team ID.
        3. Verify the updater is a member of the team.
        4. If ``assignee_to_id`` is being changed, verify they are a member.
        5. Apply the update.

    Args:
        task_id: The UUID of the task to update.
        schema: The validated update request.
        current_user: The authenticated user performing the update.
        session: The active database session.

    Returns:
        The updated ``Task`` ORM instance.

    Raises:
        TaskNotFoundException: If the task does not exist.
        ValueError: If updater or new assignee is not a team member.
    """
    task_repo = TaskRepository(session=session)
    project_repo = ProjectRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch task and project
    task = await _get_task(task_id=task_id, session=session)
    project = await project_repo.get_by_id(id=task.project_id)
    
    if project is None or project.team_id is None:
        raise ValueError("Task is attached to an invalid project.")

    # Step 1.5: Verfiy updater role
    updater_role = await member_repo.get_member_role(
        member_id=current_user.id,
        team_id=project.team_id
    )

    if updater_role not in {UserRoles.SUPER_ADMIN, UserRoles.ADMIN}:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 2: Verify updater is a member
    is_updater_member = await member_repo.check_if_membership(
        member_id=current_user.id,
        team_id=project.team_id,
    )
    if not is_updater_member:
        raise ValueError("Must be a member of the project's team to update tasks.")


    # Step 3: Verify new assignee is a member (if provided)
    if schema.assignee_to_id:
        is_assignee_member = await member_repo.check_if_membership(
            member_id=schema.assignee_to_id,
            team_id=project.team_id,
        )
        if not is_assignee_member:
            raise ValueError("Assignee must be a member of the project's team.")



    # Step 4: Apply update
    updated_task = await task_repo.update(
        orm_model=task,
        update_data=schema.model_dump(exclude_unset=True),
    )

    return updated_task


async def soft_delete_task(
    task_id: ID,
    current_user: User,
    session: AsyncSession,
) -> Task:
    """Soft-deletes a task by setting ``is_active`` to ``False``.

    Orchestration steps:
        1. Fetch the task.
        2. Fetch the project to verify team membership.
        3. Verify the user is a team member.
        4. Deactivate the task.

    Args:
        task_id: The UUID of the task to delete.
        current_user: The authenticated user performing the deletion.
        session: The active database session.

    Returns:
        The soft-deleted ``Task`` ORM instance.
    """
    task_repo = TaskRepository(session=session)
    project_repo = ProjectRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch task and project
    task = await _get_task(task_id=task_id, session=session)
    project = await project_repo.get_by_id(id=task.project_id)

    if project is None or project.team_id is None:
        raise ValueError("Task is attached to an invalid project.")

    # Step 2: Verify deleter is a member
    is_member = await member_repo.check_if_membership(
        member_id=current_user.id,
        team_id=project.team_id,
    )
    if not is_member:
        raise ValueError("Must be a member of the project's team to delete tasks.")

    # Step 3: Apply the soft delete
    deleted_task = await task_repo.update(
        orm_model=task,
        update_data={'is_active': False},
    )

    return deleted_task


async def list_project_tasks(
    project_id: ID,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[Task]:
    """Lists all active tasks within a project.

    Args:
        project_id: The UUID of the project.
        session: The active database session.
        skip: Number of records to skip. Defaults to ``0``.
        limit: Maximum number of records to return. Defaults to ``20``.

    Returns:
        A list of active ``Task`` ORM instances.
    """
    task_repo = TaskRepository(session=session)

    return await task_repo.get_project_tasks(
        project_id=project_id,
        skip=skip,
        limit=limit,
    )


async def list_user_assigned_tasks(
    user_id: ID,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[Task]:
    """Lists all active tasks assigned to a user across all projects.

    Args:
        user_id: The UUID of the user.
        session: The active database session.
        skip: Number of records to skip. Defaults to ``0``.
        limit: Maximum number of records to return. Defaults to ``20``.

    Returns:
        A list of assigned ``Task`` ORM instances.
    """
    task_repo = TaskRepository(session=session)

    return await task_repo.get_user_assigned_tasks(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
