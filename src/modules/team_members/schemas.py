from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID as ID

from src.database import UserRoles


class AddMemberRequest(BaseModel):

    user_id: ID
    """UUID of the user to add to the team"""

    role: UserRoles = Field(default=UserRoles.DEVELOPER)
    """Role to assign to the new member"""


class UpdateMemberRoleRequest(BaseModel):

    role: UserRoles
    """The new role to assign"""

class MemberResponse(BaseModel):

    # To enable ORM validate -> ModelClass.model_validate(orm_instance)
    model_config = ConfigDict(from_attributes=True)

    member_id: ID
    team_id: ID
    role: UserRoles
    is_active: bool
    joined_at: datetime




