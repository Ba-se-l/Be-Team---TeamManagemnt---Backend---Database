from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID


from src.database import BaseRepository
from src.database import UserRoles
from src.modules.team_members.models import TeamMember



class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self, session:AsyncSession):
        super().__init__(model=TeamMember, session=session)

    
    async def get_membership(self, member_id:ID, team_id:ID) -> TeamMember | None:
        """Retrieves a specific membership record by composite `PK`"""
        return await self.get_one_by_attribute(member_id=member_id, team_id=team_id)
    
    async def check_if_membership(self, member_id:ID, team_id:ID):
        """Checks if a user is a membership of a specific teaam. O(1) via composite `PK`"""
        return await self.get_membership(member_id=member_id, team_id=team_id) is not None
    
    async def get_team_members(self, team_id:ID, skip:int = 0, limit:int = 20) -> list[TeamMember]:
        """Retrevies all members of a specific team"""
        stmt = (
            select(TeamMember)
            .where(self.model.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
    
    async def get_user_memberships(self, member_id: ID, skip: int= 0, limit: int=20) -> list[TeamMember]:
        """Retrives all team memberships for a specific user"""
        stmt = (
            select(TeamMember)
            .where(self.model.member_id == member_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
    
    async def get_member_role(self, member_id: ID, team_id: ID) -> UserRoles | None:
        """Retrives the role of a specific member in a specific team"""
        membership = await self.get_membership(member_id=member_id, team_id=team_id)
        return membership.role if membership else None
    
    