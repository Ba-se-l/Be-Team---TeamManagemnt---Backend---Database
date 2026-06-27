from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID


from src.database import BaseRepository
from src.modules.team.models import Team


class TeamRepository(BaseRepository[Team]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Team, session=session)

    async def get_active_teams(self, skip:int = 0, limit:int = 20) -> list[Team]:
        """Retrieves paginated list of active temas"""
        stmt = (
            select(Team)
            .where(self.model.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
    
    async def get_teams_by_creator(self, creator_id: ID, skip:int = 0, limit:int = 20) -> list[Team]:
        """Retrieves all teams created by a specific user"""
        stmt = (
            select(Team)
            .where(self.model.creator_id == creator_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())