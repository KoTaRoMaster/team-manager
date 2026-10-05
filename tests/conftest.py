import datetime
import uuid

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.database import Base
from app.dependencies import get_async_session
from app.enums import UserRole
from app.main import app
from app.models import User, Team
from app.schemas import TeamCreate, TaskCreate, MeetingCreate
from app.security import hash_password
from app.services import TaskService
from app.services.team_service import TeamService

TEST_DB_URL = 'postgresql+asyncpg://postgres:12345@localhost:5432/team_manager_test'


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)

    async with engine.connect() as connection:

        outer_trans = await connection.begin()

        session = AsyncSession(bind=connection, expire_on_commit=False)

        await session.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(sess, trans):
            if trans.nested and not trans._parent.nested:
                sess.begin_nested()

        try:
            yield session
        finally:
            await session.close()
            await outer_trans.rollback()
            await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = _override_get_async_session

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://localhost:8000/api/',
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_factory(db_session):
    async def _create_user(role: str = UserRole.MANAGER, **overrides):
        defaults = dict(
            name=f'user-{uuid.uuid4().hex[:6]}',
            email=f'{uuid.uuid4().hex[:8]}@example.com',
            hashed_password=hash_password('Test1234!'),
            role=role
        )
        defaults.update(overrides)
        user = User(**defaults)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def auth_headers_factory(client, user_factory):
    async def _create_auth(role=UserRole.MANAGER, **user_overrides):
        user = await user_factory(role=role, **user_overrides)
        response = await client.post(
            'auth/login',
            json={'email': user.email, 'password': 'Test1234!'}
        )
        assert response.status_code == 200, f"login failed: {response.text}"

        token = response.json()['access_token']

        return {"Authorization": f"Bearer {token}"}, user

    return _create_auth


@pytest_asyncio.fixture
async def team_factory(db_session):
    async def _crate_team(user: User, name: str = 'Test team'):
        service = TeamService(db_session)
        team = await service.create_team(TeamCreate(name=name), user.id)
        return team

    return _crate_team


@pytest_asyncio.fixture
async def test_team(db_session, user_factory, team_factory):
    return await team_factory(await user_factory())


@pytest_asyncio.fixture
async def task_factory(db_session):
    async def _create_task(user: User, team: Team, **overrides):
        service = TaskService(db_session)
        defaults = dict(
            title='Test task',
            description='Testing task'
        )
        defaults.update(overrides)
        task_data = TaskCreate(**defaults)
        task = await service.create_task(task_data, team.id, user.id)
        return task

    return _create_task


@pytest_asyncio.fixture
async def meeting_factory(db_session):
    async def _create_meeting(organizer: User, team: Team, participant_ids, **overrides):
        service = TaskService(db_session)
        defaults = dict(
            title='Test meeting',
            starts_at=datetime.datetime.now(),
            ends_at=datetime.datetime.now() + datetime.timedelta(hours=1),
            participant_ids=participant_ids if participant_ids else [],
        )
        defaults.update(overrides)
        meeting_data = MeetingCreate(**defaults)
        meeting = await service.create_meeting(meeting_data, team.id, organizer.id)
        return meeting

    return _create_meeting


@pytest_asyncio.fixture
async def team_join(db_session, client):
    async def _create_join(headers: dict, team: Team):
        join = await client.post(f'teams/{team.id}/join', headers=headers, json={'invite_code': team.invite_code})
        assert join.status_code == 201, f"join failed: {join.text}"

    return _create_join
