"""User module public API.

Exposes ORM models, exceptions, repositories, schemas, and the FastAPI router.
"""

from .models import User
from .repository import UserRepository
from .exceptions import UserNotFoundException, UserAlreadyExistsException, UserInactiveException
from .schemas import UserResponse
from .router import router

__all__ = (
    # from models.py
    'User',

    # from repository.py
    'UserRepository',

    # from exceptions.py
    'UserNotFoundException',
    'UserAlreadyExistsException',
    'UserInactiveException',

    # from schemas.py
    'UserResponse',

    # from router.py
    'router',
)