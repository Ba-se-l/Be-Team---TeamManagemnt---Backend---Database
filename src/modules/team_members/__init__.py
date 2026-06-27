"""Team Members module public API.

Exposes ORM models, exceptions, repositories, and the FastAPI router.
"""

from .models import TeamMember
from .repository import TeamMemberRepository
from .exceptions import TeamMemberNotFoundException, TeamMemberInactiveException, InsufficientRoleException
from .router import router

__all__ = (
    # from models.py
    'TeamMember',

    # from repository.py
    'TeamMemberRepository',

    # from exceptions.py
    'TeamMemberNotFoundException',
    'TeamMemberInactiveException',
    'InsufficientRoleException',

    # from router.py
    'router',
)