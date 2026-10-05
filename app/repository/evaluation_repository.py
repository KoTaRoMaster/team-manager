from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing_extensions import override

from app.models import Evaluation, Task
from app.repository.base_crud import BaseCrud


class EvaluationRepository(BaseCrud):
    def __init__(self, session):
        super().__init__(session, Evaluation)

    @override
    async def get_by_id(self, task_id) -> Evaluation | None:
        result = await self.session.execute(
            select(Evaluation)
            .where(Evaluation.task_id == task_id)
        )
        return result.scalars().first()

    async def get_received_evaluations(self, user_id: int) -> list[Evaluation]:
        result = await self.session.execute(
            select(Evaluation)
            .join(Task, Task.id == Evaluation.task_id)
            .where(Task.assignee_id == user_id)
            .options(
                joinedload(Evaluation.task)
            )
        )
        return list(result.scalars().all())
