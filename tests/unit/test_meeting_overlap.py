import datetime

import pytest
from unittest.mock import MagicMock, AsyncMock

from fastapi import HTTPException
from app.services import TaskService
pytestmark = pytest.mark.unit


def make_service() -> TaskService:
    service = TaskService.__new__(TaskService)
    service.session = AsyncMock()
    return service

def fake_execute_result(ids: list[int]) -> MagicMock:
    result = MagicMock()
    result.scalars.return_value.all.return_value = ids
    return result


class TestCheckOverlapsMeeting:
    async def test_success_not_raise(self):
        service = make_service()
        service.session.execute.return_value = fake_execute_result([])

        starts = datetime.datetime(2026, 10,5,10,0)
        ends = datetime.datetime(2026, 10,5,11,0)

        await service._check_overlaps_meeting({1,2}, starts, ends)
        service.session.execute.assert_awaited_once()


    async def test_conflict_raises_409_with_user_id(self):
        service = make_service()
        service.session.execute.return_value = fake_execute_result([2])

        starts = datetime.datetime(2026, 10,5,10,0)
        ends = datetime.datetime(2026, 10,5,11,0)

        with pytest.raises(HTTPException) as exc_info:
            await service._check_overlaps_meeting({1,2}, starts, ends)
        assert exc_info.value.status_code == 409
        assert "2" in exc_info.value.detail

    async def test_multiple_conflicts_raises_409_with_user_ids(self):
        service = make_service()
        service.session.execute.return_value = fake_execute_result([3,7])

        starts = datetime.datetime(2026, 10,5,10,0)
        ends = datetime.datetime(2026, 10,5,11,0)

        with pytest.raises(HTTPException) as exc_info:
            await service._check_overlaps_meeting({1,3,6,7}, starts, ends)

        assert exc_info.value.status_code == 409
        assert "3" in exc_info.value.detail
        assert "7" in exc_info.value.detail