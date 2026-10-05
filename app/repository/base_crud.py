from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


class BaseCrud:
    def __init__(self, session: AsyncSession, Model: type[Base]):
        self.session = session
        self.Model = Model

    async def create(self, data: dict):
        model_db = self.Model(**data)
        self.session.add(model_db)

        await self.session.flush()
        return model_db

    async def get_all(self):
        result = await self.session.execute(
            select(self.Model)
        )
        return result.scalars().all()

    async def get_by_id(self, id):
        return await self.session.get(self.Model, id)

    async def delete(self, model):
        return await self.session.delete(model)

    async def update(self, model, data):
        for field in data:
            if hasattr(model, field):
                setattr(model, field, data[field])
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model
