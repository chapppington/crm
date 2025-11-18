from uuid import UUID

from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import (
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as UUIDType
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class OrganizationMemberModel(TimedBaseModel):
    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_organization_member"),)

    organization_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("organizations.oid", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("users.oid", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    organization: Mapped["OrganizationModel"] = relationship(  # noqa: F821
        "OrganizationModel",
        back_populates="members",
        lazy="selectin",
    )
    user: Mapped["UserModel"] = relationship(  # noqa: F821
        "UserModel",
        back_populates="organization_members",
        lazy="selectin",
    )
