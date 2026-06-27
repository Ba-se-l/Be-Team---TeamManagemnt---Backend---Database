from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID as ID

class CreateTeamRequest(BaseModel):

    name: str = Field(..., min_length=5, max_length=100)
    description: str | None = Field(default=None, max_length=500)



class UpdateTeamRequest(BaseModel):

    name: str | None = Field(default=None, min_length=5, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class TeamResponse(BaseModel):

    # To enable ORM validate -> ModelClass.model_validate(orm_instance)
    model_config = ConfigDict(from_attributes=True)

    id: ID
    name: str
    description: str | None
    is_active: bool
    creator_id: ID | None
    created_at: datetime
    updated_at: datetime
