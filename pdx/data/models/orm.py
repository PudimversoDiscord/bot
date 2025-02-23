from sqlalchemy import Index
from sqlalchemy.orm import (
    MappedAsDataclass,
    DeclarativeBase,
    Mapped,
    mapped_column
)


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True, ):
    pass


class MarkovTransition(Base):
    """Transições de estados para o modelo de Markov."""
    __tablename__ = "markov_transitions"
    __table_args__ = (
        Index("ix_current_state_brin", "current_state", postgresql_using="brin"),
        Index("ix_current_next_covering", "current_state", "next_state", "count"),
    )

    current_state: Mapped[str] = mapped_column(primary_key=True)
    next_state: Mapped[str] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(
        default=1, nullable=False, index=True
    )
