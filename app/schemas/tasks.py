import datetime

from pydantic import BaseModel, Field

from app.enums import TaskStatus
from app.schemas.base import ORMBase
from app.schemas.evaluations import EvaluationResponse


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    assignee_id: int | None = None
    due_date: datetime.date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    assignee_id: int | None = None
    due_date: datetime.date | None = None
    status: TaskStatus | None = None


class TaskResponse(ORMBase):
    id: int
    team_id: int
    title: str
    description: str | None
    assignee_id: int | None
    assignee_name: str | None = None
    status: TaskStatus
    due_date: datetime.date | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    evaluation: EvaluationResponse | None = None

    @classmethod
    def from_orm_task(cls, task) -> TaskResponse:
        return cls(
            id=task.id,
            team_id=task.team_id,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assignee_name=task.assignee.name if task.assignee else None,
            status=task.status,
            due_date=task.due_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
            evaluation=EvaluationResponse.model_validate(task.evaluation) if task.evaluation else None,
        )
