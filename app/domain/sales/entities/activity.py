from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.sales.value_objects.activity import (
    ActivityPayloadValueObject,
    ActivityTypeValueObject,
)


@dataclass(eq=False)
class ActivityEntity(BaseEntity):
    deal_id: UUID
    author_user_id: Optional[UUID]
    type: ActivityTypeValueObject
    payload: ActivityPayloadValueObject
