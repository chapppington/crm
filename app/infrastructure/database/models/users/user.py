from infrastructure.database.models.base import TimedBaseModel
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class UserModel(TimedBaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    organization_members: Mapped[list["OrganizationMemberModel"]] = relationship(  # noqa: F821
        "OrganizationMemberModel",
        back_populates="user",
        lazy="selectin",
    )
    owned_contacts: Mapped[list["ContactModel"]] = relationship(  # noqa: F821
        "ContactModel",
        foreign_keys="[ContactModel.owner_id]",
        back_populates="owner",
        lazy="selectin",
    )
    owned_deals: Mapped[list["DealModel"]] = relationship(  # noqa: F821
        "DealModel",
        foreign_keys="[DealModel.owner_id]",
        back_populates="owner",
        lazy="selectin",
    )
    activities: Mapped[list["ActivityModel"]] = relationship(  # noqa: F821
        "ActivityModel",
        foreign_keys="[ActivityModel.author_id]",
        back_populates="author",
        lazy="selectin",
    )
