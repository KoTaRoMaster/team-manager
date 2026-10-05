from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Team
from app.repository.base_crud import BaseCrud


class TeamRepository(BaseCrud):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Team)

    async def get_team_by_owner(self, owner_id: int) -> list[Team]:
        team = await self.session.execute(
            select(Team)
            .where(Team.owner_id == owner_id)
        )
        return list(team.scalars().all())
