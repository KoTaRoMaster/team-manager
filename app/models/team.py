import secrets

from ._shared import *


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    invite_code: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, default=lambda: secrets.token_hex(4)
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # relationship

    owner: Mapped["User"] = relationship(
        back_populates="owned_teams", foreign_keys=[owner_id]
    )

    memberships: Mapped[list["TeamMemberShip"]] = relationship(
        back_populates="team", cascade="all, delete-orphan",
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )

    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Team id={self.id} name='{self.name}' invite_code='{self.invite_code}' memberships={self.memberships}>"
