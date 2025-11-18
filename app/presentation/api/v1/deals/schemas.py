from uuid import UUID

from presentation.api.filters import PaginationOut
from pydantic import BaseModel

from domain.sales.entities import DealEntity


class DealResponseSchema(BaseModel):
    id: UUID
    organization_id: UUID
    contact_id: UUID
    owner_id: UUID
    title: str
    amount: float
    currency: str
    status: str
    stage: str
    created_at: str
    updated_at: str

    @classmethod
    def from_entity(cls, entity: DealEntity) -> "DealResponseSchema":
        return cls(
            id=entity.oid,
            organization_id=entity.organization_id,
            contact_id=entity.contact_id,
            owner_id=entity.owner_user_id,
            title=entity.title.as_generic_type(),
            amount=entity.amount.as_generic_type(),
            currency=entity.currency.as_generic_type(),
            status=entity.status.as_generic_type().value,
            stage=entity.stage.as_generic_type().value,
            created_at=entity.created_at.isoformat() if entity.created_at else "",
            updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
        )


class CreateDealRequestSchema(BaseModel):
    contact_id: UUID
    title: str
    amount: float
    currency: str


class UpdateDealRequestSchema(BaseModel):
    status: str | None = None
    stage: str | None = None


class DealListResponseSchema(BaseModel):
    items: list[DealResponseSchema]
    pagination: PaginationOut
