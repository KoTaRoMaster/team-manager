from sqlalchemy.orm import selectinload
from typing_extensions import override

from app.models import Meeting, MeetingParticipant
from app.repository.base_crud import BaseCrud

from sqlalchemy import select

class MeetingRepository(BaseCrud):
    def __init__(self, session):
        super().__init__(session, Meeting)

    @override
    async def get_by_id(self, id) -> Meeting | None:
        result = await self.session.execute(
            select(Meeting)
            .where(Meeting.id == id)
            .options(
                selectinload(Meeting.participants)
                .selectinload(MeetingParticipant.user)
            )
        )
        return result.scalars().first()


    async def get_user_meetings(self, user_id: int) -> list[Meeting]:
        result = await self.session.execute(
            select(Meeting)
            .join(MeetingParticipant, MeetingParticipant.meeting_id == Meeting.id)
            .where(MeetingParticipant.user_id == user_id)
            .options(
                selectinload(Meeting.participants)
                .selectinload(MeetingParticipant.user)
            )
        )
        return list(result.scalars().all())

    async def get_team_meetings(self, team_id: int) -> list[Meeting]:
        result = await self.session.execute(
            select(Meeting)
            .where(Meeting.team_id == team_id)
            .options(
                selectinload(Meeting.participants)
                .selectinload(MeetingParticipant.user)
            )
        )
        return list(result.scalars().all())