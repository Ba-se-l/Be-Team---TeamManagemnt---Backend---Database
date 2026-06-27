"""Root module initialization.

Aggregates all routers from the various domain modules into a single
``api_router`` that can be included in ``main.py``.
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .user import router as user_router
from .team import router as team_router
from .team_members import router as team_members_router
from .project import team_nested_router as project_nested_router, top_level_router as project_top_router
from .task import project_nested_router as task_nested_router, top_level_router as task_top_router
from .technology import router as technology_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(team_router)
api_router.include_router(team_members_router)
api_router.include_router(project_nested_router)
api_router.include_router(project_top_router)
api_router.include_router(task_nested_router)
api_router.include_router(task_top_router)
api_router.include_router(technology_router)

__all__ = (
    'api_router',
)
