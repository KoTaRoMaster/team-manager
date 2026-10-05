import datetime

from fastapi import HTTPException

from app.repository.calendar_repository import CalendarRepository
from app.schemas import CalendarResponse


class CalendarService:
    def __init__(self, session):
        self.session = session
        self.calendar_repo = CalendarRepository(session)

    async def get_calendar(self, user_id: int, date_from: datetime.date, date_to: datetime.date) -> CalendarResponse:
        if date_from > date_to:
            raise HTTPException(status_code=404, detail="'from' не может быть позже 'to'")

        tasks = await self.calendar_repo.get_user_tasks_in_range(user_id, date_from, date_to)
        meetings = await self.calendar_repo.get_user_meetings_in_range(user_id, date_from, date_to)

        return CalendarResponse.from_orm_tasks_and_meetings(date_from, date_to, tasks, meetings)
