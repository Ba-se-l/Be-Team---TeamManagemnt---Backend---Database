from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID as ID

from src.database import BaseRepository
from src.database import TaskStatus
from src.modules.task.models import Task



class TaskRepository(BaseRepository[Task]):
    def __init__(self, session:AsyncSession):
        super().__init__(model=Task, session=session)

    async def get_project_tasks(self, project_id: ID, skip: int = 0, limit: int = 20) -> list[Task]:
        """Retrives all active tasks belonging to a specific project"""

        stmt = (
            select(Task)
            .where(
                Task.project_id == project_id,
                Task.is_active.is_(True)
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
    

    async def get_user_assigned_tasks(self, user_id: ID, skip:int = 0, limit:int = 20) -> list[Task]:
        """Retrives all tasks assigned to a specific user across all projects"""
        stmt = (
            select(Task)
            .where(Task.assignee_to_id == user_id)
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())
    

    async def get_tasks_by_status(self, project_id: ID, status: TaskStatus, skip: int = 0, limit : int = 20) -> list[Task]:
        """Retrives tasks filtered by status within a project"""
        stmt = (
            select(Task)
            .where(
                Task.project_id == project_id,
                Task.status == status
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return list(result.scalars().all())