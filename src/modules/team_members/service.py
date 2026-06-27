"""Team Members domain service layer.

Contains business logic for managing team memberships, including
adding members, removing members, updating roles, and listing team
members. Enforces role-based access control (RBAC).
"""

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID

from src.database import UserRoles
from src.modules.user import User, UserRepository, UserNotFoundException, UserInactiveException
from .models import TeamMember
from .schemas import AddMemberRequest, UpdateMemberRoleRequest
from .repository import TeamMemberRepository
from .exceptions import TeamMemberNotFoundException, InsufficientRoleException


async def add_member(
    team_id: ID,
    schema: AddMemberRequest,
    adder: User,
    session: AsyncSession,
) -> TeamMember:
    """Adds a new member to a team with a specific role.

    Orchestration steps:
        1. Verify adder has ADMIN+ role in the team.
        2. Verify the target user exists and is active.
        3. Verify the user is not already a member.
        4. Create and persist the TeamMember record.

    Args:
        team_id: The UUID of the team.
        schema: The validated request containing user_id and role.
        adder: The authenticated user attempting to add the member.
        session: The active database session.

    Returns:
        The newly created ``TeamMember`` ORM instance.

    Raises:
        InsufficientRoleException: If the adder lacks ADMIN role.
        UserNotFoundException: If the target user does not exist.
        UserInactiveException: If the target user is inactive.
        ValueError: If the user is already a member (domain rule).
    """
    member_repo = TeamMemberRepository(session=session)
    user_repo = UserRepository(session=session)

    # Step 1: Verify adder's role
    adder_role = await member_repo.get_member_role(member_id=adder.id, team_id=team_id)
    if adder_role != UserRoles.SUPER_ADMIN:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 2: Verify target user exists and is active
    target_user = await user_repo.get_by_id(id=schema.user_id)
    if target_user is None:
        raise UserNotFoundException(identifier=str(schema.user_id))
    if not target_user.is_active:
        raise UserInactiveException(identifier=str(schema.user_id))

    # Step 3: Verify user is not already a member
    is_member = await member_repo.check_if_membership(
        member_id=schema.user_id,
        team_id=team_id,
    )
    if is_member:
        raise ValueError(f"User {schema.user_id} is already a member of team {team_id}.")

    # Step 4: Create membership
    membership = TeamMember(
        member_id=schema.user_id,
        team_id=team_id,
        role=schema.role,
    )
    await member_repo.create(orm_model=membership)

    await session.flush() 

    return membership


async def remove_member(
    team_id: ID,
    user_id: ID,
    remover: User,
    session: AsyncSession,
) -> TeamMember:
    """Removes a member from a team.

    Orchestration steps:
        1. Verify remover has ADMIN+ role in the team.
        2. Fetch the target membership.
        3. Guard: Cannot remove self if SUPER_ADMIN (orphan protection).
        4. Hard-delete the membership record.

    Args:
        team_id: The UUID of the team.
        user_id: The UUID of the user to remove.
        remover: The authenticated user attempting to remove the member.
        session: The active database session.

    Returns:
        The deleted ``TeamMember`` ORM instance.

    Raises:
        InsufficientRoleException: If the remover lacks ADMIN role.
        TeamMemberNotFoundException: If the target membership does not exist.
        ValueError: If a SUPER_ADMIN tries to remove themselves.
    """
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Verify remover's role
    remover_role = await member_repo.get_member_role(member_id=remover.id, team_id=team_id)
    if remover_role != UserRoles.SUPER_ADMIN:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 2: Fetch target membership
    membership = await member_repo.get_membership(member_id=user_id, team_id=team_id)
    if membership is None:
        raise TeamMemberNotFoundException(identifier=f"User {user_id} in Team {team_id}")

    # Step 3: Guard orphan protection
    if remover.id == user_id and membership.role == UserRoles.SUPER_ADMIN:
        raise ValueError("SUPER_ADMIN cannot remove themselves. Transfer ownership first or delete the team.")

    # Step 4: Delete membership
    await member_repo.delete(orm_model=membership)

    return membership


async def update_member_role(
    team_id: ID,
    user_id: ID,
    schema: UpdateMemberRoleRequest,
    updater: User,
    session: AsyncSession,
) -> TeamMember:
    """Updates a member's role within a team.

    Orchestration steps:
        1. Verify updater has SUPER_ADMIN role in the team.
        2. Fetch the target membership.
        3. Guard: Cannot demote self.
        4. Update the role.

    Args:
        team_id: The UUID of the team.
        user_id: The UUID of the user whose role is being updated.
        schema: The validated request containing the new role.
        updater: The authenticated user attempting the update.
        session: The active database session.

    Returns:
        The updated ``TeamMember`` ORM instance.

    Raises:
        InsufficientRoleException: If the updater lacks SUPER_ADMIN role.
        TeamMemberNotFoundException: If the target membership does not exist.
        ValueError: If a SUPER_ADMIN tries to demote themselves.
    """
    member_repo = TeamMemberRepository(session=session)

    # Step 1: Verify updater's role
    updater_role = await member_repo.get_member_role(member_id=updater.id, team_id=team_id)
    if updater_role != UserRoles.SUPER_ADMIN:
        raise InsufficientRoleException('SUPER_ADMIN')

    # Step 2: Fetch target membership
    membership = await member_repo.get_membership(member_id=user_id, team_id=team_id)
    if membership is None:
        raise TeamMemberNotFoundException(identifier=f"User {user_id} in Team {team_id}")

    # Step 3: Guard self-demotion
    if updater.id == user_id and schema.role != UserRoles.SUPER_ADMIN:
        raise ValueError("SUPER_ADMIN cannot demote themselves. Transfer ownership first.")

    # Step 4: Apply update
    updated_membership = await member_repo.update(
        orm_model=membership,
        update_data={'role': schema.role},
    )

    return updated_membership


async def list_team_members(
    team_id: ID,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[TeamMember]:
    """Lists all members of a specific team with pagination.

    Args:
        team_id: The UUID of the team.
        session: The active database session.
        skip: Number of records to skip. Defaults to ``0``.
        limit: Maximum number of records to return. Defaults to ``20``.

    Returns:
        A list of ``TeamMember`` ORM instances.
    """
    member_repo = TeamMemberRepository(session=session)

    return await member_repo.get_team_members(team_id=team_id, skip=skip, limit=limit)
