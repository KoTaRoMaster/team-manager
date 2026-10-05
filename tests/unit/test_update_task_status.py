from unittest.mock import AsyncMock, patch

import pytest

from app.enums import TaskStatus
from app.exceptions import NotFoundError
from app.schemas import TaskUpdate
from app.services import TaskService

pytestmark = pytest.mark.unit


def make_service() -> TaskService:
    service = TaskService.__new__(TaskService)
    service.session = AsyncMock()
    service.task_repo = AsyncMock()
    return service


class FakeTask:
    def __init__(self, id: int = 1, team_id: int = 1):
        self.id = id
        self.team_id = team_id


class TestUpdateTaskStatus:
    async def test_assignee_change_forces_in_progress(self):
        service = make_service()
        task = FakeTask()
        service.task_repo.get_by_id.return_value = task
        service._user_is_team_owner = AsyncMock()
        service.task_repo.update.return_value = task

        with patch("app.services.task_service.TaskResponse") as mock_response:
            mock_response.from_orm_task.side_effect = lambda t: t
            await service.update_task(TaskUpdate(assignee_id=12), task_id=1, user_id=44)

        called_data = service.task_repo.update.call_args.args[1]
        assert called_data["status"] == TaskStatus.IN_PROGRESS
        assert called_data["assignee_id"] == 12

    async def test_no_assignee_change_status_untouched(self):
        service = make_service()
        task = FakeTask()
        service.task_repo.get_by_id.return_value = task
        service._user_is_team_owner = AsyncMock()
        service.task_repo.update.return_value = task

        with patch("app.services.task_service.TaskResponse") as mock_response:
            mock_response.from_orm_task.side_effect = lambda t: t
            await service.update_task(TaskUpdate(title="Новое название"), task_id=1, user_id=99)

        called_data = service.task_repo.update.call_args.args[1]
        assert "status" not in called_data

    async def test_status_override(self):
        service = make_service()
        task = FakeTask()
        service.task_repo.get_by_id.return_value = task
        service._user_is_team_owner = AsyncMock()
        service.task_repo.update.return_value = task

        with patch("app.services.task_service.TaskResponse") as mock_response:
            mock_response.from_orm_task.side_effect = lambda t: t
            await service.update_task(TaskUpdate(assignee_id=42, status=TaskStatus.DONE), task_id=1, user_id=99)

        called_data = service.task_repo.update.call_args.args[1]
        assert called_data["status"] == TaskStatus.IN_PROGRESS

    async def test_task_not_found_raises(self):
        service = make_service()
        service.task_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.update_task(TaskUpdate(title="x"), task_id=999, user_id=1)