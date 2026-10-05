from ._shared import *


class MeetingParticipant(Base):
    """Чистая M:N между Meeting и User (без доп. атрибутов помимо связи)."""
    __tablename__ = "meeting_participants"
    __table_args__ = (
        UniqueConstraint("meeting_id", "user_id", name="uq_meeting_participant"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    meeting: Mapped["Meeting"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="meeting_participations")

    def __repr__(self):
        return f'<MeetingParticipant id={self.id} meeting_id={self.meeting_id}  user_id={self.user_id}>'
