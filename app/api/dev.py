from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import UserServiceDep, TaskServiceDep, TeamServiceDep
from app.schemas import TokenResponse, LoginRequest, CommentResponse, TeamResponse, TaskResponse, UserResponse, \
    EvaluationResponse

router = APIRouter(
    tags=["dev"]
)


# auth
@router.post("/auth/user/login", response_model=TokenResponse, status_code=200)
async def login_user(service: UserServiceDep, data_form: OAuth2PasswordRequestForm = Depends()):
    login_data = LoginRequest(email=data_form.username, password=data_form.password)
    return await service.login(login_data)


# teams
@router.get("/teams", response_model=list[TeamResponse], status_code=200)
async def get_teams(service: TeamServiceDep):
    return await service.get_teams()


@router.get("/teams/{team_id}", response_model=TeamResponse, status_code=200)
async def get_team(team_id: int, service: TeamServiceDep):
    return await service.get_team_by_id(team_id)


@router.delete("/teams/{team_id}", status_code=204)
async def delete_team(team_id: int, service: TeamServiceDep):
    await service.delete_team(team_id)


# tasks
@router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
async def get_task(task_id: int, service: TaskServiceDep):
    return await service.get_task(task_id)


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse], status_code=200)
async def get_comments(task_id: int, service: TaskServiceDep):
    return await service.get_task_comments(task_id)


@router.get('/tasks/{task_id}/evaluation', response_model=EvaluationResponse, status_code=200)
async def get_evaluation(task_id: int, service: TaskServiceDep):
    return await service.get_evaluation(task_id)


# users
@router.get("/users", response_model=list[UserResponse], status_code=200)
async def get_users(service: UserServiceDep):
    return await service.get_users()


@router.get("/users/{id}", response_model=UserResponse, status_code=200)
async def get_user(id: int, service: UserServiceDep):
    return await service.get_user_by_id(id)


@router.delete("/users/{id}", status_code=200)
async def delete_user(id: int, service: UserServiceDep):
    await service.delete_user(id)
