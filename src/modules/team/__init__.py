"""Team module public API.

Exposes ORM models, exceptions, repositories, and the FastAPI router.
"""

from .models import Team
from .repository import TeamRepository
from .exceptions import TeamNotFoundException, TeamAlreadyExistsException, TeamInactiveException
from .router import router

__all__ = (
    # from models.py
    'Team',

    # from repository.py
    'TeamRepository',

    # from exceptions.py
    'TeamNotFoundException',
    'TeamAlreadyExistsException',
    'TeamInactiveException',

    # from router.py
    'router',
)