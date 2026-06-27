from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID as ID

from src.database import TaskPriority, TaskStatus

class CreateTaskRequest(BaseModel):

    title: str = Field(..., min_length=10, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    deadline: datetime | None = Field(default=None)
    assignee_to_id: ID | None = Field(default=None)

class UpdateTasksRequest(BaseModel):

    title: str | None = Field(default=None, min_length=10, max_length=100)
    description: str | None = Field(default=None, min_length=10, max_length=500)
    status: TaskStatus | None = Field(default=None)
    priority: TaskPriority | None = Field(default=None)
    deadline: datetime | None = Field(default=None)
    assignee_to_id: ID | None = Field(default=None)

class TaskResponse(BaseModel):

    # To enable ORM validate -> ModelClass.model_validate(orm_instance)
    model_config = ConfigDict(from_attributes=True)

    id: ID
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    deadline: datetime | None
    is_active: bool
    creator_id: ID | None
    assignee_to_id: ID | None
    project_id: ID
    created_at: datetime
    updated_at: datetime