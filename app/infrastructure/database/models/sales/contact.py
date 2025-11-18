from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class ContactModel(TimedBaseModel):
    __tablename__ = "contacts"

    organization_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("organizations.oid", ondelete="RESTRICT"),
        nullable=False,
    )
    owner_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("users.oid", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    organization: Mapped["OrganizationModel"] = relationship(  # noqa: F821
        "OrganizationModel",
        back_populates="contacts",
        lazy="selectin",
    )
    owner: Mapped["UserModel"] = relationship(  # noqa: F821
        "UserModel",
        foreign_keys=[owner_id],
        back_populates="owned_contacts",
        lazy="selectin",
    )
    deals: Mapped[list["DealModel"]] = relationship(  # noqa: F821
        "DealModel",
        back_populates="contact",
        lazy="selectin",
    )
