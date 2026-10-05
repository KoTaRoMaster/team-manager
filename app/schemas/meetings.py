import datetime

from pydantic import BaseModel, Field, field_validator, EmailStr

from app.schemas.base import ORMBase


class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    participant_ids: list[int] = Field(default_factory=list)

    @field_validator("ends_at")
    @classmethod
    def ends_after_starts(cls, v, info):
        starts_at = info.data.get("starts_at")
        if starts_at and v <= starts_at:
            raise ValueError("ends_at должен быть позже starts_at")
        return v


class MeetingParticipantResponse(ORMBase):
    id: int  # user_id
    name: str
    email: EmailStr


class MeetingResponse(ORMBase):
    id: int
    team_id: int
    organizer_id: int
    title: str
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    participants: list[MeetingParticipantResponse] = Field(default_factory=list)
    created_at: datetime.datetime

    @classmethod
    def from_orm_meeting(cls, meeting) -> MeetingResponse:
        return cls(
            id=meeting.id,
            team_id=meeting.team_id,
            organizer_id=meeting.organizer_id,
            title=meeting.title,
            starts_at=meeting.starts_at,
            ends_at=meeting.ends_at,
            participants=[
                MeetingParticipantResponse(id=p.user.id, name=p.user.name, email=p.user.email)
                for p in meeting.participants
            ],
            created_at=meeting.created_at,
        )


class MeetingConflictError(BaseModel):
    """Тело ответа 409 при пересечении встреч по времени."""
    detail: str = "У одного или нескольких участников уже есть встреча в это время"
    conflicting_user_ids: list[int]
