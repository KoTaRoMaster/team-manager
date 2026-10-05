import datetime

from fastapi import APIRouter
from fastapi import Query

from app.dependencies import CalendarServiceDep, CurrentUserDep
from app.schemas import CalendarResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=CalendarResponse, status_code=200)
async def get_calendar(
        service: CalendarServiceDep,
        current_user: CurrentUserDep,
        date_from: datetime.date = Query(..., alias="from"),
        date_to: datetime.date = Query(..., alias="to"),
):
    return await service.get_calendar(current_user.id, date_from, date_to)
