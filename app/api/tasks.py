from fastapi import APIRouter

from app.dependencies import TaskServiceDep, require_roles, CurrentUserDep
from app.enums import UserRole
from app.models import User
from app.schemas import TaskUpdate, CommentResponse, CommentCreate, EvaluationCreate

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.patch("/{task_id}", status_code=200)
async def update_task(task_data: TaskUpdate, task_id: int, service: TaskServiceDep,
                      user: User = require_roles(UserRole.MANAGER)):
    return await service.update_task(task_data, task_id, user.id)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, service: TaskServiceDep,
                      _: User = require_roles(UserRole.MANAGER)):
    return await service.delete_task(task_id)


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(comment_data: CommentCreate, task_id: int, service: TaskServiceDep,
                         user: CurrentUserDep):
    return await service.create_comment(comment_data, task_id, user.id)


@router.post("/{task_id}/evaluation", status_code=201)
async def set_evaluation(evaluation_data: EvaluationCreate, task_id: int, service: TaskServiceDep,
                         user: User = require_roles(UserRole.MANAGER)):
    return await service.set_evaluation(evaluation_data, task_id, user.id)
