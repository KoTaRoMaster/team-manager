from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing_extensions import override

from app.models import TeamMemberShip
from app.repository.base_crud import BaseCrud


class TeamMemberShipRepository(BaseCrud):
    def __init__(self, session: AsyncSession):
        super().__init__(session, TeamMemberShip)

    @override
    async def create(self, data: dict):
        membership = TeamMemberShip(**data)
        self.session.add(membership)

        await self.session.flush()

        result = await self.session.execute(
            select(TeamMemberShip)
            .where(TeamMemberShip.id == membership.id)
            .options(
                selectinload(TeamMemberShip.user)
            )
        )
        return result.scalar_one_or_none()

    async def get_team_membership(self, team_id: int) -> list[TeamMemberShip]:
        team_membership = await self.session.execute(
            select(TeamMemberShip)
            .where(TeamMemberShip.team_id == team_id)
            .options(
                selectinload(TeamMemberShip.user)
            )
        )
        return list(team_membership.scalars().all())

    async def get_member(self, user_id: int, team_id: int) -> TeamMemberShip | None:
        member = await self.session.execute(
            select(TeamMemberShip)
            . where(TeamMemberShip.user_id == user_id,
                    TeamMemberShip.team_id == team_id
            )
            .options(
                selectinload(TeamMemberShip.user)
            )
        )

        return member.scalars().first()
