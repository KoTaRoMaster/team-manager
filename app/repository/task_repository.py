from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing_extensions import override

from app.models import Task
from app.repository.base_crud import BaseCrud


class TaskRepository(BaseCrud):
    def __init__(self, session):
        super().__init__(session, Task)

    @override
    async def create(self, data: dict) -> Task:
        task = Task(**data)
        self.session.add(task)

        await self.session.flush()

        result = await self.session.execute(
            select(Task)
            .where(Task.id == task.id)
            .options(
                selectinload(Task.assignee),
                        selectinload(Task.evaluation)
            )
        )
        return result.scalars().first()

    @override
    async def get_all(self, team_id: int = None) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .where(Task.team_id == team_id)
            .options(
                selectinload(Task.assignee),
                selectinload(Task.evaluation)
            )
        )
        return list(result.scalars().all())

    @override
    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.session.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.assignee),
                selectinload(Task.evaluation)
            )
        )
        return result.scalars().first()


    async def get_user_tasks(self, user_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .where(Task.assignee_id == user_id)
            .options(
                selectinload(Task.assignee),
                selectinload(Task.evaluation)
            )
        )
        return list(result.scalars().all())