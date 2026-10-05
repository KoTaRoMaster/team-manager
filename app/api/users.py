from fastapi import APIRouter

from app.dependencies import UserServiceDep, CurrentUserDep
from app.schemas import MyEvaluationsSummary, MeetingResponse, UserResponse, PasswordChange, TaskResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, status_code=200)
async def get_profile(service: UserServiceDep, current_user: CurrentUserDep):
    return await service.get_profile(current_user)


@router.put("/me/password", status_code=204)
async def reset_password(user_data: PasswordChange, service: UserServiceDep, current_user: CurrentUserDep):
    return await service.reset_password(current_user.id, user_data)


@router.get("/me/evaluations", response_model=MyEvaluationsSummary, status_code=200)
async def get_evaluations(service: UserServiceDep, current_user: CurrentUserDep):
    return await service.get_my_evaluations(current_user.id)


@router.get("/me/meetings", response_model=list[MeetingResponse], status_code=200)
async def get_meetings(service: UserServiceDep, current_user: CurrentUserDep):
    return await service.get_my_meetings(current_user.id)


@router.get("/me/tasks", response_model=list[TaskResponse], status_code=200)
async def get_tasks(service: UserServiceDep, current_user: CurrentUserDep):
    return await service.get_my_tasks(current_user.id)