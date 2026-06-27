"""Team domain service layer.

Contains all business logic for team management operations including
creation, update, soft-deletion, and listing of user teams.
Each function orchestrates calls to ``TeamRepository`` and
``TeamMemberRepository``, enforcing role-based access control.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID

from src.database import UserRoles
from src.modules.user import User
from src.modules.team_members import TeamMemberRepository, InsufficientRoleException
from src.modules.team_members.models import TeamMember
from .models import Team
from .schemas import CreateTeamRequest, UpdateTeamRequest
from .repository import TeamRepository
from .exceptions import TeamNotFoundException


async def _get_team(team_id: ID, session: AsyncSession) -> Team:
    """Internal helper: fetches a team by ID or raises.

    Args:
        team_id: The UUID of the team to fetch.
        session: The active database session.

    Returns:
        The ``Team`` ORM instance.

    Raises:
        TeamNotFoundException: If no team with the given ID exists.
    """
    repo = TeamRepository(session=session)
    team = await repo.get_by_id(id=team_id)

    if team is None:
        raise TeamNotFoundException(identifier=str(team_id))

    return team


async def create_team(
    schema: CreateTeamRequest,
    current_user: User,
    session: AsyncSession,
) -> Team:
    """Creates a new team and assigns the creator as SUPER_ADMIN member.

    Orchestration steps:
        1. Build the ``Team`` ORM instance with the creator's ID.
        2. Persist the team via ``TeamRepository.create``.
        3. Build a ``TeamMember`` record with ``SUPER_ADMIN`` role.
        4. Persist the membership via ``TeamMemberRepository.create``.

    Args:
        schema: The validated team creation request.
        current_user: The authenticated user creating the team.
        session: The active database session.

    Returns:
        The newly created ``Team`` ORM instance.
    """
    team_repo = TeamRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Build the Team ORM model
    team = Team(
        name=schema.name,
        description=schema.description,
        creator_id=current_user.id,
    )

    # Step 2: Persist the team
    team = await team_repo.create(orm_model=team)

    await session.flush() # مشان نستخدم المعرّف الخاص بالفريق لانشاء صاحب الفريق او يلي عمل الفريق ك `TEAM_LEADER`

    # Step 3: Build the creator's membership as ADMIN
    membership = TeamMember(
        member_id=current_user.id,
        team_id=team.id,
        role=UserRoles.SUPER_ADMIN,
    )

    # Step 4: Persist the membership
    await member_repo.create(orm_model=membership)

    await session.flush()

    return team


async def update_team(
    team_id: ID,
    schema: UpdateTeamRequest,
    current_user: User,
    session: AsyncSession,
) -> Team:
    """Updates a team's details.

    Only users with ``ADMIN`` or ``SUPER_ADMIN`` role in the team
    are allowed to update it.

    Orchestration steps:
        1. Fetch the team by ID.
        2. Verify the user has ``ADMIN+`` role in the team.
        3. Apply the update via repository.

    Args:
        team_id: The UUID of the team to update.
        schema: The validated update request with optional fields.
        current_user: The authenticated user performing the update.
        session: The active database session.

    Returns:
        The updated ``Team`` ORM instance.

    Raises:
        TeamNotFoundException: If the team does not exist.
        InsufficientRoleException: If the user lacks ``ADMIN`` role.
    """
    team_repo = TeamRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch the team
    team = await _get_team(team_id=team_id, session=session)

    # Step 2: Verify the user has ADMIN+ role
    member_role = await member_repo.get_member_role(
        member_id=current_user.id,
        team_id=team_id,
    )
    if member_role != UserRoles.SUPER_ADMIN:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 3: Apply the update
    updated_team = await team_repo.update(
        orm_model=team,
        update_data=schema.model_dump(exclude_unset=True),
    )

    return updated_team


async def soft_delete_team(
    team_id: ID,
    current_user: User,
    session: AsyncSession,
) -> Team:
    """Soft-deletes a team by setting ``is_active`` to ``False``.

    Only users with ``SUPER_ADMIN`` role in the team are allowed
    to soft-delete it. The team record and all memberships remain
    in the database for referential integrity.

    Args:
        team_id: The UUID of the team to deactivate.
        current_user: The authenticated user performing the deletion.
        session: The active database session.

    Returns:
        The soft-deleted ``Team`` ORM instance.

    Raises:
        TeamNotFoundException: If the team does not exist.
        InsufficientRoleException: If the user lacks ``SUPER_ADMIN`` role.
    """
    team_repo = TeamRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Fetch the team
    team = await _get_team(team_id=team_id, session=session)

    # Step 2: Verify the user has SUPER_ADMIN role
    member_role = await member_repo.get_member_role(
        member_id=current_user.id,
        team_id=team_id,
    )
    if member_role != UserRoles.SUPER_ADMIN:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 3: Deactivate via update
    soft_deleted_team = await team_repo.update(
        orm_model=team,
        update_data={'is_active': False},
    )

    return soft_deleted_team


async def list_user_teams(
    user_id: ID,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[Team]:
    """Lists all teams that a user is a member of.

    Orchestration steps:
        1. Fetch all ``TeamMember`` records for the user.
        2. Extract the ``team_id`` from each membership.
        3. Fetch the corresponding ``Team`` objects.

    Args:
        user_id: The UUID of the user whose teams to list.
        session: The active database session.
        skip: Number of memberships to skip. Defaults to ``0``.
        limit: Maximum number of memberships to return. Defaults to ``20``.

    Returns:
        A list of ``Team`` ORM instances the user belongs to.
    """
    team_repo = TeamRepository(session=session)
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Get all memberships for this user
    memberships = await member_repo.get_user_memberships(
        member_id=user_id,
        skip=skip,
        limit=limit,
    )

    # Step 2: Extract team IDs
    team_ids = [m.team_id for m in memberships]

    if not team_ids:
        return []

    # Step 3: Fetch teams by IDs
    teams = []
    for team_id in team_ids:
        team = await team_repo.get_by_id(id=team_id)
        if team is not None:
            teams.append(team)

    return teams