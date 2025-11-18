from typing import Any
from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID as UUIDType,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class ActivityModel(TimedBaseModel):
    __tablename__ = "activities"

    deal_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("deals.oid", ondelete="CASCADE"),
        nullable=False,
    )
    author_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("users.oid", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    deal: Mapped["DealModel"] = relationship(  # noqa: F821
        "DealModel",
        back_populates="activities",
        lazy="selectin",
    )
    author: Mapped["UserModel | None"] = relationship(  # noqa: F821
        "UserModel",
        foreign_keys=[author_id],
        back_populates="activities",
        lazy="selectin",
    )
