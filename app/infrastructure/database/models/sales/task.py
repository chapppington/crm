from datetime import date
from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class TaskModel(TimedBaseModel):
    __tablename__ = "tasks"

    deal_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("deals.oid", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    deal: Mapped["DealModel"] = relationship(  # noqa: F821
        "DealModel",
        back_populates="tasks",
        lazy="selectin",
    )
