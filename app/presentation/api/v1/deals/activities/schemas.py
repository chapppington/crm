from uuid import UUID

from pydantic import BaseModel

from domain.sales.entities import ActivityEntity


class ActivityResponseSchema(BaseModel):
    id: UUID
    deal_id: UUID
    author_id: UUID | None
    type: str
    payload: dict
    created_at: str

    @classmethod
    def from_entity(cls, entity: ActivityEntity) -> "ActivityResponseSchema":
        return cls(
            id=entity.oid,
            deal_id=entity.deal_id,
            author_id=entity.author_user_id,
            type=entity.type.as_generic_type().value,
            payload=entity.payload.as_generic_type(),
            created_at=entity.created_at.isoformat() if entity.created_at else "",
        )


class CreateCommentRequestSchema(BaseModel):
    text: str


class ActivityListResponseSchema(BaseModel):
    items: list[ActivityResponseSchema]
