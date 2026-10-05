from ._shared import *


class Meeting(Base):
    __tablename__ = 'meetings'
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_meeting_end_after_start"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'), index=True, nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )

    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    team: Mapped["Team"] = relationship(back_populates="meetings")
    organizer: Mapped["User"] = relationship(
        back_populates="organized_meetings", foreign_keys=[organizer_id]
    )

    participants: Mapped[list["MeetingParticipant"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Meeting id={self.id} team_id={self.team_id} organizer_id={self.organizer_id}, title={self.title}>"
