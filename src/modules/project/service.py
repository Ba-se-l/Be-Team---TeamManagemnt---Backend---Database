"""Project domain service layer.

Contains business logic for managing projects within teams,
including creation, update, soft-deletion, and listing.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID

from src.database import UserRoles, ProjectStatus
from src.modules.user import User
from src.modules.team_members import TeamMemberRepository, InsufficientRoleException
from .models import Project
from .schemas import CreateProjectRequest, UpdateProjectRequest
from .repository import ProjectRepository
from .exceptions import ProjectNotFoundException


async def _get_project(project_id: ID, session: AsyncSession) -> Project:
    """Internal helper: fetches a project by ID or raises.

    Args:
        project_id: The UUID of the project to fetch.
        session: The active database session.

    Returns:
        The ``Project`` ORM instance.

    Raises:
        ProjectNotFoundException: If no project with the given ID exists.
    """
    repo = ProjectRepository(session=session)
    project = await repo.get_by_id(id=project_id)

    if project is None:
        raise ProjectNotFoundException(identifier=str(project_id))

    return project


async def create_project(
    team_id: ID,
    schema: CreateProjectRequest,
    creator: User,
    session: AsyncSession,
) -> Project:
    """Creates a new project within a team.

    Orchestration steps:
        1. Verify the creator has ADMIN+ role in the team.
        2. Build the ``Project`` ORM instance.
        3. Persist the project via ``ProjectRepository.create``.

    Args:
        team_id: The UUID of the team that will own the project.
        schema: The validated project creation request.
        creator: The authenticated user creating the project.
        session: The active database session.

    Returns:
        The newly created ``Project`` ORM instance.

    Raises:
        InsufficientRoleException: If the creator lacks ADMIN role.
    """
    project_repo = ProjectRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Verify creator's role in the team
    creator_role = await member_repo.get_member_role(member_id=creator.id, team_id=team_id)
    if creator_role not in {UserRoles.SUPER_ADMIN, UserRoles.ADMIN}:
        raise InsufficientRoleException('ADMIN')

    # Step 2: Build the ORM model
    project = Project(
        title=schema.title,
        short_description=schema.short_description,
        deadline=schema.deadline,
        creator_id=creator.id,
        team_id=team_id,
        status=ProjectStatus.TODO,
    )

    # Step 3: Persist and return
    project = await project_repo.create(orm_model=project)

    await session.flush()
    
    return project


async def update_project(
    project_id: ID,
    schema: UpdateProjectRequest,
    current_user: User,
    session: AsyncSession,
) -> Project:
    """Updates a project's details.

    Orchestration steps:
        1. Fetch the project by ID.
        2. Verify the updater has ADMIN+ role in the project's team.
        3. Apply the update via repository.

    Args:
        project_id: The UUID of the project to update.
        schema: The validated update request with optional fields.
        current_user: The authenticated user performing the update.
        session: The active database session.

    Returns:
        The updated ``Project`` ORM instance.

    Raises:
        ProjectNotFoundException: If the project does not exist.
        InsufficientRoleException: If the updater lacks ADMIN role.
    """
    project_repo = ProjectRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch the project
    project = await _get_project(project_id=project_id, session=session)

    if project.team_id is None:
        raise ValueError("Project is not attached to any team.")

    # Step 2: Verify updater's role
    updater_role = await member_repo.get_member_role(
        member_id=current_user.id,
        team_id=project.team_id,
    )
    if updater_role not in {UserRoles.SUPER_ADMIN, UserRoles.ADMIN}:
        raise InsufficientRoleException('ADMIN')

    # Step 3: Apply the update
    updated_project = await project_repo.update(
        orm_model=project,
        update_data=schema.model_dump(exclude_unset=True),
    )

    return updated_project


async def soft_delete_project(
    project_id: ID,
    current_user: User,
    session: AsyncSession,
) -> Project:
    """Soft-deletes a project by setting ``is_active`` to ``False``.

    Orchestration steps:
        1. Fetch the project by ID.
        2. Verify the deleter has SUPER_ADMIN role in the project's team.
        3. Deactivate the project.

    Args:
        project_id: The UUID of the project to delete.
        current_user: The authenticated user performing the deletion.
        session: The active database session.

    Returns:
        The soft-deleted ``Project`` ORM instance.

    Raises:
        ProjectNotFoundException: If the project does not exist.
        InsufficientRoleException: If the deleter lacks SUPER_ADMIN role.
    """
    project_repo = ProjectRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch the project
    project = await _get_project(project_id=project_id, session=session)

    if project.team_id is None:
        raise ValueError("Project is not attached to any team.")

    # Step 2: Verify deleter's role
    deleter_role = await member_repo.get_member_role(
        member_id=current_user.id,
        team_id=project.team_id,
    )
    if deleter_role != UserRoles.SUPER_ADMIN:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 3: Apply the soft delete
    deleted_project = await project_repo.update(
        orm_model=project,
        update_data={'is_active': False},
    )

    return deleted_project


async def list_team_projects(
    team_id: ID,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[Project]:
    """Lists all active projects within a specific team.

    Args:
        team_id: The UUID of the team.
        session: The active database session.
        skip: Number of records to skip. Defaults to ``0``.
        limit: Maximum number of records to return. Defaults to ``20``.

    Returns:
        A list of active ``Project`` ORM instances.
    """
    project_repo = ProjectRepository(session=session)

    return await project_repo.get_team_projects(
        team_id=team_id,
        skip=skip,
        limit=limit,
    )
