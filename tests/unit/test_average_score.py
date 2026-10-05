from unittest.mock import AsyncMock, patch

import pytest

from app.services import UserService

pytestmark = pytest.mark.unit

def make_service() -> UserService:
    service = UserService.__new__(UserService)
    service.evaluation_repo = AsyncMock()
    return service


class FakeEvaluation:
    def __init__(self, score: int):
        self.score = score


class TestGetMyEvaluations:
    async def test_success(self):
        service = make_service()
        service.evaluation_repo.get_received_evaluations.return_value = [
            FakeEvaluation(5), FakeEvaluation(4), FakeEvaluation(4)
        ]
        with patch("app.services.user_service.MyEvaluationResponse") as mock_resp, \
             patch("app.services.user_service.MyEvaluationsSummary") as mock_summary:
            mock_resp.from_orm_evaluation.side_effect = lambda e: e
            await service.get_my_evaluations(user_id=1)

        _, kwargs = mock_summary.call_args

        assert kwargs["average_score"] == pytest.approx(13/3)
        assert len(kwargs["evaluations"]) == 3

    async def test_single_evaluation_average_equals_its_score(self):
        service = make_service()
        service.evaluation_repo.get_received_evaluations.return_value = [FakeEvaluation(5)]

        with patch("app.services.user_service.MyEvaluationResponse") as mock_resp, \
             patch("app.services.user_service.MyEvaluationsSummary") as mock_summary:
            mock_resp.from_orm_evaluation.side_effect = lambda e: e
            await service.get_my_evaluations(user_id=1)

        _, kwargs = mock_summary.call_args
        assert kwargs["average_score"] == 5

    async def test_no_evaluations_average_is_zero(self):
        service = make_service()
        service.evaluation_repo.get_received_evaluations.return_value = []

        with patch("app.services.user_service.MyEvaluationResponse") as mock_resp, \
             patch("app.services.user_service.MyEvaluationsSummary") as mock_summary:
            mock_resp.from_orm_evaluation.side_effect = lambda e: e
            await service.get_my_evaluations(user_id=1)

        _, kwargs = mock_summary.call_args
        assert kwargs["average_score"] == 0
        assert kwargs["evaluations"] == []