import datetime

from pydantic import BaseModel

from app.enums import TaskStatus
from app.models import Task, Meeting


class CalendarTaskItem(BaseModel):
    id: int
    title: str
    due_date: datetime.date
    status: TaskStatus


class CalendarMeetingItem(BaseModel):
    id: int
    title: str
    starts_at: datetime.datetime
    ends_at: datetime.datetime


class CalendarResponse(BaseModel):
    from_date: datetime.date
    to_date: datetime.date
    tasks: list[CalendarTaskItem]
    meetings: list[CalendarMeetingItem]

    @classmethod
    def from_orm_tasks_and_meetings(cls, date_from: datetime.date, date_to: datetime.date, tasks: list[Task],
                                    meetings: list[Meeting]) -> CalendarResponse:
        return cls(
            from_date=date_from,
            to_date=date_to,
            tasks=[
                CalendarTaskItem(
                    id=task.id, title=task.title, due_date=task.due_date, status=task.status
                )
                for task in tasks
            ],
            meetings=[
                CalendarMeetingItem(
                    id=meeting.id, title=meeting.title, starts_at=meeting.starts_at, ends_at=meeting.ends_at
                )
                for meeting in meetings
            ],
        )
