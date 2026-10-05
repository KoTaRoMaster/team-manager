from typing_extensions import override

from app.models import MeetingParticipant
from app.repository.base_crud import BaseCrud


class MeetingParticipantRepository(BaseCrud):
    def __init__(self, session):
        super().__init__(session, MeetingParticipant)

    @override
    async def create(self, data: dict) -> MeetingParticipant:
        participant = MeetingParticipant(**data)
        self.session.add(participant)

        await self.session.flush()
        return participant
