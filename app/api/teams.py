from fastapi import APIRouter

from app.dependencies import TeamServiceDep, require_roles, CurrentUserDep, TaskServiceDep
from app.enums import UserRole
from app.models import User
from app.schemas import TeamCreate, TeamResponse, TeamJoin, TeamMemberResponse, MemberRoleUpdate, TaskCreate, \
    MeetingResponse
from app.schemas.meetings import MeetingCreate
from app.schemas.tasks import TaskResponse

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamResponse, status_code=201)
async def create_team(team_data: TeamCreate, service: TeamServiceDep,
                      user: User = require_roles(UserRole.MANAGER, UserRole.ADMIN)):
    return await service.create_team(team_data, user.id)


# @router.get("/my", response_model=list[TeamResponse], status_code=200)
# async def get_my_teams(service: TeamServiceDep, user: User = require_roles(UserRole.MANAGER)):
#     return await service.get_my_teams(user.id)


# @router.delete("/my/{team_id}", status_code=204)
# async def delete_my_team(team_id: int, service: TeamServiceDep, user: User = require_roles(UserRole.MANAGER)):
#     await service.delete_my_team(team_id, user.id)

@router.post("/{team_id}/join", status_code=201)
async def team_join(team_id: int, code: TeamJoin, service: TeamServiceDep, current_user: CurrentUserDep):
    return await service.team_join(team_id, code, current_user.id)


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse], status_code=200)
async def get_team_members(team_id: int, service: TeamServiceDep, _: CurrentUserDep):
    return await service.get_team_members(team_id)


# members

@router.patch("/{team_id}/members/{member_id}", response_model=TeamMemberResponse, status_code=200)
async def member_role_update(role_data: MemberRoleUpdate, team_id: int, member_id: int, service: TeamServiceDep,
                             user: User = require_roles(UserRole.MANAGER)):
    return await service.member_role_update(role_data, team_id, member_id, user.id)


@router.delete("/{team_id}/members/{member_id}", status_code=204)
async def team_member_delete(team_id: int, member_id: int, service: TeamServiceDep,
                             user: User = require_roles(UserRole.MANAGER)):
    return await service.team_member_delete(team_id, member_id, user.id)


# task
@router.post("/{team_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate, team_id: int, service: TaskServiceDep,
                      user: User = require_roles(UserRole.MANAGER)):
    return await service.create_task(task_data, team_id, user.id)


@router.get("/{team_id}/tasks", response_model=list[TaskResponse], status_code=200)
async def get_tasks(team_id: int, service: TaskServiceDep,
                    user: User = require_roles(UserRole.MEMBER, UserRole.MANAGER)):
    return await service.get_tasks(team_id, user.id)


# meeting

@router.post("/{team_id}/meetings", response_model=MeetingResponse, status_code=201)
async def create_meeting(meeting_data: MeetingCreate, team_id: int, service: TaskServiceDep,
                         user: CurrentUserDep):
    return await service.create_meeting(meeting_data, team_id, user.id)


@router.get('/{team_id}/meetings', response_model=list[MeetingResponse], status_code=200)
async def get_meetings(team_id: int, service: TaskServiceDep,
                       user: CurrentUserDep):
    return await service.get_meetings(team_id, user.id)


@router.delete("/{team_id}/meetings/{meeting_id}", status_code=204)
async def cancel_meeting(team_id: int, meeting_id: int, service: TaskServiceDep,
                         user: CurrentUserDep):
    return await service.cancel_meeting(team_id, meeting_id, user.id)
