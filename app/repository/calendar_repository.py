import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, Meeting, MeetingParticipant


class CalendarRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_tasks_in_range(self, user_id: int, date_from: datetime.date, date_to: datetime.date) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .where(
                Task.assignee_id == user_id,
                Task.due_date.is_not(None),
                Task.due_date >= date_from,
                Task.due_date <= date_to
            )
        )
        return list(result.scalars().all())

    async def get_user_meetings_in_range(self, user_id: int, date_from: datetime.date, date_to: datetime.date) -> list[Meeting]:
        starts_day = datetime.datetime.combine(date_from, datetime.datetime.min.time())
        ends_day = datetime.datetime.combine(date_to, datetime.datetime.max.time())
        result = await self.session.execute(
            select(Meeting)
            .join(Meeting.participants)
            .where(
                MeetingParticipant.user_id == user_id,
                Meeting.starts_at >= starts_day,
                Meeting.ends_at <= ends_day
            )
        )
        return list(result.scalars().all())
