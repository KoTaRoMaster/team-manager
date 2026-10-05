import datetime

from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import TaskStatus
from app.exceptions import NotFoundError
from app.models import TeamMemberShip, Team, Meeting, MeetingParticipant
from app.repository import TaskRepository, TeamRepository, CommentRepository, TeamMemberShipRepository, \
    EvaluationRepository, MeetingRepository, MeetingParticipantRepository, UserRepository
from app.schemas import TaskCreate, TaskResponse, TaskUpdate, CommentCreate, CommentResponse, EvaluationCreate, \
    EvaluationResponse, MeetingCreate, MeetingResponse


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.team_repo = TeamRepository(session)
        self.team_member_repo = TeamMemberShipRepository(session)
        self.comment_repo = CommentRepository(session)
        self.evaluation_repo = EvaluationRepository(session)
        self.meetings_repo = MeetingRepository(session)
        self.participant_repo = MeetingParticipantRepository(session)
        self.user_repo = UserRepository(session)

    async def _team_exist(self, team_id: int) -> None:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundError('team_id', team_id)

    async def _user_in_team(self, team_id: int, user_id: int) -> None:
        team_members = await self.team_member_repo.get_member(user_id, team_id)
        if not team_members:
            raise HTTPException(status_code=403,
                                detail=f'Пользователь с id={user_id} не является членом команды с id={team_id}')

    async def _user_is_team_owner(self, user_id: int, team_id: int) -> None:
        result = await self.session.execute(
            select(Team)
            .where(Team.id == team_id,
                   Team.owner_id == user_id
                   )
        )
        if not result.scalars().first():
            raise HTTPException(status_code=403, detail=f'Вы не являетесь создателем команды')

    async def _task_exist(self, task_id: int) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError('team_id', task_id)

    async def _validate_participants_in_team(self, team_id: int, user_ids: set[int]) -> None:
        result = await self.session.execute(
            select(TeamMemberShip.user_id)
            .where(TeamMemberShip.team_id == team_id,
                   TeamMemberShip.user_id.in_(user_ids),
                   ))
        found_ids = set(result.scalars().all())

        missing = user_ids - found_ids
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Пользователи не состоят в этой команде: {sorted(missing)}",
            )

    async def _check_overlaps_meeting(self, user_ids: set[int], starts_at: datetime.datetime,
                                      ends_at: datetime.datetime) -> None:
        result = await self.session.execute(
            select(MeetingParticipant.user_id)
            .join(Meeting, Meeting.id == MeetingParticipant.meeting_id)
            .where(
                or_(
                    and_(starts_at <= Meeting.starts_at, Meeting.starts_at <= ends_at),
                    and_(starts_at <= Meeting.ends_at, Meeting.ends_at <= ends_at)
                )
            )
            .where(MeetingParticipant.user_id.in_(user_ids))
        )
        overlaps_ids = result.scalars().all()
        if overlaps_ids:
            raise HTTPException(409, f"У сотрудников {overlaps_ids} уже назначены встречи в это время")

    async def get_tasks(self, team_id: int, user_id: int) -> list[TaskResponse]:
        await self._team_exist(team_id)
        await self._user_in_team(team_id, user_id)
        tasks = await self.task_repo.get_all(team_id)
        return [TaskResponse.from_orm_task(task) for task in tasks]

    async def get_task(self, task_id: int) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError('task_id', task_id)
        return TaskResponse.from_orm_task(task)

    async def create_task(self, task_data: TaskCreate, team_id: int, user_id: int) -> TaskResponse:
        await self._team_exist(team_id)
        await self._user_is_team_owner(user_id, team_id)

        data = task_data.model_dump(exclude_unset=True) | {'team_id': team_id}
        if 'assignee_id' in data:
            await self._user_in_team(team_id, data['assignee_id'])
            data['status'] = TaskStatus.IN_PROGRESS
        task = await self.task_repo.create(data)
        await self.session.commit()
        return TaskResponse.from_orm_task(task)

    async def update_task(self, task_data: TaskUpdate, task_id: int, user_id: int) -> TaskResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError('task_id', task_id)
        await self._user_is_team_owner(user_id, task.team_id)

        data = task_data.model_dump(exclude_unset=True)

        if 'assignee_id' in data:
            data['status'] = TaskStatus.IN_PROGRESS
        updated_task = await self.task_repo.update(task, data)
        await self.session.commit()
        return TaskResponse.from_orm_task(updated_task)

    async def delete_task(self, task_id: int) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError('task_id', task_id)
        await self.task_repo.delete(task)
        await self.session.commit()

    async def create_comment(self, comment_data: CommentCreate, task_id: int, author_id: int) -> CommentResponse:
        await self._task_exist(task_id)
        data = comment_data.model_dump() | {'task_id': task_id, 'author_id': author_id}
        comment = await self.comment_repo.create(data)
        await self.session.commit()
        return CommentResponse.from_orm_comment(comment)

    async def get_task_comments(self, task_id: int) -> list[CommentResponse]:
        await self._task_exist(task_id)
        comments = await self.comment_repo.get_all(task_id)
        return [CommentResponse.from_orm_comment(comment) for comment in comments]

    async def set_evaluation(self, evaluation_data: EvaluationCreate, task_id: int, evaluator_id: int) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError('task_id', task_id)

        if task.status != TaskStatus.DONE:
            raise HTTPException(status_code=400, detail=f"Оценивать можно задачи только которые 'done'")

        await self.session.refresh(task, attribute_names=['team'])
        if task.team.owner_id != evaluator_id:
            raise HTTPException(status_code=403, detail=f'Вы не являетесь создателем этой команды.')

        evaluation = await self.evaluation_repo.get_by_id(task_id)
        if evaluation:
            raise HTTPException(status_code=409, detail=f'Оценка уже выставлена на данную задачу.')

        data = evaluation_data.model_dump(exclude_unset=True) | {'task_id': task_id, 'evaluator_id': evaluator_id}
        await self.evaluation_repo.create(data)
        await self.session.commit()

    async def get_evaluation(self, task_id: int) -> EvaluationResponse:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError('task_id', task_id)
        evaluation = await self.evaluation_repo.get_by_id(task_id)
        return EvaluationResponse.model_validate(evaluation)

    async def create_meeting(self, meeting_data: MeetingCreate, team_id: int, organizer_id: int) -> MeetingResponse:
        await self._team_exist(team_id)
        await self._user_in_team(team_id, organizer_id)

        data = meeting_data.model_dump(exclude_unset=True) | {
            'team_id': team_id, 'organizer_id': organizer_id
        }
        all_user_ids = set(data.pop('participant_ids', [])) | {organizer_id}

        await self._validate_participants_in_team(team_id, all_user_ids)
        await self._check_overlaps_meeting(all_user_ids, data['starts_at'], data['ends_at'])

        meeting = await self.meetings_repo.create(data)
        for uid in all_user_ids:
            await self.create_meeting_participant(uid, meeting.id)
        await self.session.commit()

        meeting = await self.meetings_repo.get_by_id(meeting.id)
        return MeetingResponse.from_orm_meeting(meeting)

    async def create_meeting_participant(self, user_id: int, meeting_id: int) -> MeetingParticipant:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError('user_id', user_id)
        data = {'user_id': user_id, 'meeting_id': meeting_id}
        participant = await self.participant_repo.create(data)
        return participant

    async def get_meetings(self, team_id: int, user_id: int) -> list[MeetingResponse]:
        await self._team_exist(team_id)
        await self._user_in_team(team_id, user_id)
        meetings = await self.meetings_repo.get_team_meetings(team_id)
        return [MeetingResponse.from_orm_meeting(meeting) for meeting in meetings]

    async def cancel_meeting(self, team_id: int, meeting_id: int, user_id: int) -> None:
        await self._team_exist(team_id)
        meeting = await self.meetings_repo.get_by_id(meeting_id)
        if not meeting:
            raise NotFoundError('meeting_id', meeting_id)
        if meeting.organizer_id != user_id:
            raise HTTPException(403, f'Только создатель встречи может её отменить.')
        await self.session.delete(meeting)
        await self.session.commit()
