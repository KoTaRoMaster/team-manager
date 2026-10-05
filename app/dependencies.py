from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.enums import UserRole
from app.models import User
from app.security import verify_token
from app.services import UserService, TeamService, TaskService
from app.services.calendar_service import CalendarService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/user/login")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_team_service(session: AsyncSession = Depends(get_async_session)):
    return TeamService(session)


TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]


async def get_current_user(service: UserServiceDep, token=Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    id = payload.get("id")
    if id is None:
        raise credentials_exception

    user = await service.get_user_by_id(id)
    if user is None:
        raise credentials_exception
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_task_service(session: AsyncSession = Depends(get_async_session)):
    return TaskService(session)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def require_roles(*roles: UserRole):
    async def check_role(current_user: CurrentUserDep) -> User:
        if current_user.role not in roles:
            raise HTTPException(403, "Недостаточно прав.")
        return current_user

    return Depends(check_role)


async def get_calendar_service(session: AsyncSession = Depends(get_async_session)):
    return CalendarService(session)


CalendarServiceDep = Annotated[CalendarService, Depends(get_calendar_service)]
