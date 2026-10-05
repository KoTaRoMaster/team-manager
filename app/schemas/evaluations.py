import datetime

from pydantic import BaseModel, Field

from app.models import Evaluation
from app.schemas.base import ORMBase


class EvaluationCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class EvaluationResponse(ORMBase):
    id: int
    task_id: int
    evaluator_id: int
    score: int
    comment: str | None
    created_at: datetime.datetime


class MyEvaluationResponse(ORMBase):
    """GET /users/me/evaluations — оценки сотрудника + средний балл."""
    task_id: int
    task_title: str
    score: int
    comment: str | None
    created_at: datetime.datetime

    @classmethod
    def from_orm_evaluation(cls, evaluation: Evaluation) -> MyEvaluationResponse:
        return cls(
            task_id=evaluation.task_id,
            task_title=evaluation.task.title,
            score=evaluation.score,
            comment=evaluation.comment,
            created_at=evaluation.created_at,
        )


class MyEvaluationsSummary(BaseModel):
    average_score: float | None
    evaluations: list[MyEvaluationResponse]
