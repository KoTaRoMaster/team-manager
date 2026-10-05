from app.enums import TeamRole
from ._shared import *


class TeamMemberShip(Base):
    __tablename__ = "team_memberships"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_membership"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    role: Mapped[TeamRole] = mapped_column(
        Enum(TeamRole, name='team_role'), default=TeamRole.MEMBER, nullable=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    team: Mapped["Team"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")

    def __repr__(self):
        return f"<TeamMemberShip id={self.id} team_id={self.team_id} user_id={self.user_id}, role={self.role}>"
