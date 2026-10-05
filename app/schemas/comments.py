import datetime

from pydantic import BaseModel, Field

from app.models import Comment
from app.schemas.base import ORMBase


class CommentCreate(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class CommentResponse(ORMBase):
    id: int
    task_id: int
    author_id: int
    author_name: str | None = None
    text: str
    created_at: datetime.datetime

    @classmethod
    def from_orm_comment(cls, comment: Comment) -> CommentResponse:
        return cls(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            author_name=comment.author.name if comment.author else None,
            text=comment.text,
            created_at=comment.created_at,
        )
