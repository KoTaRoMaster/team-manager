from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.enums import TeamRole
from app.exceptions import NotFoundError, DuplicateError
from app.repository import TeamMemberShipRepository
from app.repository import TeamRepository
from app.schemas import TeamCreate, TeamResponse, TeamJoin, TeamMemberResponse, MemberRoleUpdate


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repo = TeamRepository(session)
        self.team_members_repo = TeamMemberShipRepository(session)

    async def create_team(self, team: TeamCreate, owner_id: int) -> TeamResponse:
        data = {**team.model_dump(), 'owner_id': owner_id}
        team = await self.team_repo.create(data)
        await self.create_team_member(team.id, owner_id, TeamRole.MANAGER)
        await self.session.commit()
        return TeamResponse.model_validate(team)

    async def create_team_member(self, team_id: int, user_id: int,
                                 role: TeamRole = TeamRole.MEMBER) -> TeamMemberResponse:
        data = {'team_id': team_id, 'user_id': user_id, 'role': role}
        team_member = await self.team_members_repo.create(data)
        await self.session.commit()
        return TeamMemberResponse.from_orm_membership(team_member)

    async def team_join(self, team_id: int, join_data: TeamJoin, user_id: int) -> None:
        team = await self.get_team_by_id(team_id)
        if team.invite_code != join_data.invite_code:
            raise HTTPException(status_code=400, detail="Неправильный код приглашения")
        members = await self.team_members_repo.get_team_membership(team_id)
        if user_id in [member.user_id for member in members]:
            raise DuplicateError('team', f'user_id={user_id}')
        await self.create_team_member(team_id, user_id)

    async def get_teams(self) -> list[TeamResponse]:
        teams = await self.team_repo.get_all()
        return [TeamResponse.model_validate(team) for team in teams]

    async def get_team_by_id(self, team_id: int) -> TeamResponse:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundError('team', team_id)
        return TeamResponse.model_validate(team)

    async def get_my_teams(self, user_id: int) -> list[TeamResponse]:
        teams = await self.team_repo.get_team_by_owner(user_id)
        if not teams:
            raise NotFoundError('owner_id', user_id)
        return [TeamResponse.model_validate(team) for team in teams]

    async def get_team_members(self, team_id: int) -> list[TeamMemberResponse]:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundError('team', team_id)
        team_members = await self.team_members_repo.get_team_membership(team_id)
        return [TeamMemberResponse.from_orm_membership(t_m) for t_m in team_members]

    async def delete_team(self, team_id) -> None:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundError('team', team_id)
        await self.team_repo.delete(team)
        await self.session.commit()

    async def delete_my_team(self, team_id: int, user_id: int) -> None:
        team = await self.team_repo.get_by_id(team_id)
        if not team or team.owner_id != user_id:
            raise NotFoundError('team', team_id)
        await self.delete_team(team.id)

    async def member_role_update(self, role_data: MemberRoleUpdate, team_id: int, member_id: int,
                                 owner_id: int) -> TeamMemberResponse:
        team = await self.team_repo.get_by_id(team_id)
        if not team or team.owner_id != owner_id:
            raise NotFoundError('team', team_id)
        member = await self.team_members_repo.get_member(member_id, team_id)
        member.role = role_data.role
        await self.session.commit()
        await self.session.refresh(member)
        return TeamMemberResponse.from_orm_membership(member)

    async def team_member_delete(self, team_id: int, member_id: int, owner_id: int) -> None:
        team = await self.team_repo.get_by_id(team_id)
        if not team or team.owner_id != owner_id:
            raise NotFoundError('team', team_id)
        member = await self.team_members_repo.get_member(member_id, team_id)
        await self.session.delete(member)
        await self.session.commit()
