from fastapi import APIRouter

from app.dependencies import UserServiceDep
from app.schemas.users import UserResponse, UserCreate, TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, service: UserServiceDep):
    return await service.create_user(user)


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login_user(service: UserServiceDep, data_form: LoginRequest):
    return await service.login(data_form)
