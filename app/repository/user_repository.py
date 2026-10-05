from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from .base_crud import BaseCrud


class UserRepository(BaseCrud):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str | EmailStr) -> User | None:
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
        )
        return result.scalars().first()
