from uuid import UUID

from presentation.api.filters import PaginationOut
from pydantic import BaseModel

from domain.sales.entities import ContactEntity


class ContactResponseSchema(BaseModel):
    id: UUID
    organization_id: UUID
    owner_id: UUID
    name: str
    email: str | None
    phone: str | None
    created_at: str

    @classmethod
    def from_entity(cls, entity: ContactEntity) -> "ContactResponseSchema":
        return cls(
            id=entity.oid,
            organization_id=entity.organization_id,
            owner_id=entity.owner_user_id,
            name=entity.name.as_generic_type(),
            email=entity.email.as_generic_type() if entity.email.as_generic_type() else None,
            phone=entity.phone.as_generic_type() if entity.phone.as_generic_type() else None,
            created_at=entity.created_at.isoformat() if entity.created_at else "",
        )


class CreateContactRequestSchema(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None


class ContactListResponseSchema(BaseModel):
    items: list[ContactResponseSchema]
    pagination: PaginationOut
