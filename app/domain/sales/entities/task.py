from dataclasses import dataclass
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.sales.value_objects.task import (
    TaskDescriptionValueObject,
    TaskDueDateValueObject,
    TaskTitleValueObject,
)


@dataclass(eq=False)
class TaskEntity(BaseEntity):
    deal_id: UUID
    title: TaskTitleValueObject
    description: TaskDescriptionValueObject
    due_date: TaskDueDateValueObject
    is_done: bool = False
