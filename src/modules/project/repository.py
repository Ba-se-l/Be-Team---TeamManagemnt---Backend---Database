from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID

from src.database import BaseRepository
from src.modules.project.models import Project


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session:AsyncSession):
        super().__init__(model=Project, session=session)

    async def get_team_projects(self, team_id: ID, skip: int=0, limit : int=20) -> list[Project]:
        """Retrives all active projects belonging to a specific team"""
        stmt = (
            select(Project)
            .where(
                Project.team_id == team_id,
                Project.is_active.is_(True)
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
    
    async def get_projects_by_creator(self, creator_id: ID, skip: int=0, limit: int=20) -> list[Project]:
        """Retrives all projects created by a specific user"""

        stmt = (
            select(Project)
            .where(Project.creator_id == creator_id)
            .offset(skip)
            .limit(limit)    
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())


