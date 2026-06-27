from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from uuid import UUID as ID

from src.database import UserStatus, JobTitle


class CreateUserRequest(BaseModel):
    """Schema for user registration request"""

    name: str = Field(..., min_length=1, max_length=100)
    """The user's full name"""

    email: str = Field(..., min_length=5, max_length=100, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    """Them user's email address, `Must` be uniqe"""

    password: str = Field(..., min_length=8, max_length=100)
    """The user's plain-text password. Will be hashed before storage"""


class UpdateSchemaRequest(BaseModel):
    """Schema for updating user profile"""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    """Updated full name"""

    job_title: JobTitle | None = Field(default=None)
    """Updated job title"""

    bio: str | None = Field(default=None, max_length=500)
    """Updated biography"""


class ChangePasswordRequest(BaseModel):
    """Schema for password change request"""

    old_password: str = Field(..., min_length=8)
    """Current password for verification"""

    new_password: str = Field(..., min_length=8, max_length=100)
    """New password to set"""



class UserResponse(BaseModel):
    """Schema for user data in API responses, Exclude sensitive fields"""

    # To enable ORM validate -> ModelClass.model_validate(orm_instance)
    model_config = ConfigDict(from_attributes=True)


    id: ID
    name: str
    email: str
    is_active: bool
    is_super_admin: bool
    status: UserStatus
    job_title: JobTitle | None
    bio: str | None
    created_at: datetime
    updated_at: datetime





