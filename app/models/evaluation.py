from ._shared import *


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="ck_evaluation_score_range"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"), unique=True, index=True, nullable=False
    )
    evaluator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    score: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    task: Mapped["Task"] = relationship(back_populates="evaluation")
    evaluator: Mapped["User"] = relationship(back_populates="evaluations_given")

    def __repr__(self):
        return f'<Evaluation id={self.id} task_id={self.task_id} evaluator_id={self.evaluator_id} score={self.score}>'
