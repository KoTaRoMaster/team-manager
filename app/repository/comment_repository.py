from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing_extensions import override

from app.models import Comment
from app.repository.base_crud import BaseCrud


class CommentRepository(BaseCrud):
    def __init__(self, session):
        super().__init__(session, Comment)

    @override
    async def create(self, data: dict) -> Comment:
        comment = Comment(**data)
        self.session.add(comment)
        await self.session.flush()

        result = await self.session.execute(
            select(Comment)
            .where(Comment.id == comment.id)
            .options(
                selectinload(Comment.author)
            )
        )

        return result.scalar_one()

    @override
    async def get_all(self, task_id: int = None) -> list[Comment]:
        result = await self.session.execute(
            select(Comment).
            where(Comment.task_id == task_id)
            . options(
                selectinload(Comment.author)
            )
        )
        return list(result.scalars().all())
