from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class OrganizationModel(TimedBaseModel):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    members: Mapped[list["OrganizationMemberModel"]] = relationship(  # noqa: F821
        "OrganizationMemberModel",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    contacts: Mapped[list["ContactModel"]] = relationship(  # noqa: F821
        "ContactModel",
        back_populates="organization",
        lazy="selectin",
    )
    deals: Mapped[list["DealModel"]] = relationship(  # noqa: F821
        "DealModel",
        back_populates="organization",
        lazy="selectin",
    )
