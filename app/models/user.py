from app.enums import UserRole
from ._shared import *


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.MEMBER, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    owned_teams: Mapped[list["Team"]] = relationship(
        back_populates='owner', foreign_keys="Team.owner_id"
    )

    memberships: Mapped["TeamMemberShip"] = relationship(
        back_populates='user', cascade="all, delete, delete-orphan",
    )

    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates='assignee', foreign_keys="Task.assignee_id"
    )

    comments: Mapped[list["Comment"]] = relationship(back_populates='author')

    evaluations_given: Mapped[list["Evaluation"]] = relationship(back_populates='evaluator')

    organized_meetings: Mapped[list["Meeting"]] = relationship(
        back_populates='organizer', foreign_keys="Meeting.organizer_id"
    )

    meeting_participations: Mapped[list["MeetingParticipant"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f'<User id={self.id}, name={self.name}, email={self.email}, role={self.role}>'
