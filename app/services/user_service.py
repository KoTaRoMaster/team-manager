from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import DuplicateError, NotFoundError, LoginError, PasswordResetError
from app.models import User
from app.repository import UserRepository, EvaluationRepository, MeetingRepository, TaskRepository
from app.schemas import MyEvaluationsSummary, MyEvaluationResponse, UserCreate, UserResponse, PasswordChange, \
    TokenResponse, LoginRequest, MeetingResponse, TaskResponse
from app.security import hash_password, verify_password, create_access_token


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.meeting_repo = MeetingRepository(session)
        self.task_repo = TaskRepository(session)

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        exist = await self.user_repo.get_by_email(user_data.email)
        if exist:
            raise DuplicateError('email', user_data.email)
        hashed_password = hash_password(user_data.password)
        user = {
            "name": user_data.name,
            "email": user_data.email,
            "hashed_password": hashed_password}
        user = await self.user_repo.create(user)
        await self.session.commit()
        return user

    async def get_users(self) -> list[UserResponse]:
        users = await self.user_repo.get_all()
        return [UserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError('user', user_id)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError('user', user_id)
        await self.user_repo.delete(user)
        await self.session.commit()

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise LoginError('Неправильная почта или пароль')
        return TokenResponse(access_token=create_access_token({"id": user.id}))

    async def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    async def reset_password(self, user_id: int, user_data: PasswordChange) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError('user', user_id)
        if verify_password(user_data.password, user.hashed_password):
            raise PasswordResetError('Нельзя вводить предыдущий пароль')
        user.hashed_password = hash_password(user_data.password)
        await self.session.commit()
        await self.session.refresh(user)

    async def get_my_evaluations(self, user_id: int) -> MyEvaluationsSummary:
        evaluations = await self.evaluation_repo.get_received_evaluations(user_id)
        avg_score = sum(e.score for e in evaluations) / len(evaluations) if evaluations else 0
        evaluation_response = [MyEvaluationResponse.from_orm_evaluation(evaluation) for evaluation in evaluations]
        return MyEvaluationsSummary(evaluations=evaluation_response, average_score=avg_score)

    async def get_my_meetings(self, user_id: int) -> list[MeetingResponse]:
        meetings = await self.meeting_repo.get_user_meetings(user_id)
        return [MeetingResponse.from_orm_meeting(meeting) for meeting in meetings]

    async def get_my_tasks(self, user_id: int) -> list[TaskResponse]:
        tasks = await self.task_repo.get_user_tasks(user_id)
        return [TaskResponse.from_orm_task(task) for task in tasks]
