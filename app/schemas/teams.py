import datetime

from pydantic import BaseModel, Field, EmailStr

from app.enums import TeamRole
from app.schemas.base import ORMBase


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class TeamJoin(BaseModel):
    invite_code: str = Field(min_length=1, max_length=16)


class TeamResponse(ORMBase):
    id: int
    name: str
    invite_code: str
    owner_id: int
    created_at: datetime.datetime


class TeamMemberResponse(ORMBase):
    id: int
    name: str
    email: EmailStr
    role: TeamRole
    joined_at: datetime.datetime

    @classmethod
    def from_orm_membership(cls, membership) -> "TeamMemberResponse":
        return cls(
            id=membership.user.id,
            name=membership.user.name,
            email=membership.user.email,
            role=membership.role,
            joined_at=membership.joined_at,
        )


class MemberRoleUpdate(BaseModel):
    role: TeamRole
