from datetime import date
from uuid import UUID

from presentation.api.filters import PaginationOut
from pydantic import BaseModel

from domain.sales.entities import TaskEntity


class TaskResponseSchema(BaseModel):
    id: UUID
    deal_id: UUID
    title: str
    description: str | None
    due_date: date | None
    is_done: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_entity(cls, entity: TaskEntity) -> "TaskResponseSchema":
        return cls(
            id=entity.oid,
            deal_id=entity.deal_id,
            title=entity.title.as_generic_type(),
            description=entity.description.as_generic_type(),
            due_date=entity.due_date.as_generic_type(),
            is_done=entity.is_done,
            created_at=entity.created_at.isoformat() if entity.created_at else "",
            updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
        )


class CreateTaskRequestSchema(BaseModel):
    deal_id: UUID
    title: str
    description: str | None = None
    due_date: date | None = None


class UpdateTaskRequestSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    is_done: bool | None = None


class TaskListResponseSchema(BaseModel):
    items: list[TaskResponseSchema]
    pagination: PaginationOut
