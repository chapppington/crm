from decimal import Decimal
from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    DECIMAL,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class DealModel(TimedBaseModel):
    __tablename__ = "deals"

    organization_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("organizations.oid", ondelete="RESTRICT"),
        nullable=False,
    )
    contact_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("contacts.oid", ondelete="RESTRICT"),
        nullable=False,
    )
    owner_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("users.oid", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        DECIMAL(15, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    stage: Mapped[str] = mapped_column(String(20), nullable=False)

    organization: Mapped["OrganizationModel"] = relationship(  # noqa: F821
        "OrganizationModel",
        back_populates="deals",
        lazy="selectin",
    )
    contact: Mapped["ContactModel"] = relationship(  # noqa: F821
        "ContactModel",
        back_populates="deals",
        lazy="selectin",
    )
    owner: Mapped["UserModel"] = relationship(  # noqa: F821
        "UserModel",
        foreign_keys=[owner_id],
        back_populates="owned_deals",
        lazy="selectin",
    )
    tasks: Mapped[list["TaskModel"]] = relationship(  # noqa: F821
        "TaskModel",
        back_populates="deal",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    activities: Mapped[list["ActivityModel"]] = relationship(  # noqa: F821
        "ActivityModel",
        back_populates="deal",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
