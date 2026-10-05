
from typing import TYPE_CHECKING

from app.models._shared import *
from app.enums import TaskStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.evaluation import Evaluation


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=True
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name='task_status'), default=TaskStatus.OPEN, nullable=False
    )

    due_date: Mapped[datetime | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    team: Mapped["Team"] = relationship(back_populates="tasks")
    assignee: Mapped[User | None] = relationship(
        back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="task", cascade="all, delete-orphan", order_by="Comment.created_at"
    )
    evaluation: Mapped[Evaluation | None] = relationship(
        back_populates="task", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self):
        return f'<Task id={self.id} team_id={self.team_id} title={self.title} description={self.description} assignee_id={self.assignee_id}>'