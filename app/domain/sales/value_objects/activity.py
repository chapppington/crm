from dataclasses import dataclass
from enum import Enum
from typing import Any

from domain.base.value_object import BaseValueObject
from domain.sales.exceptions.sales import (
    EmptyActivityTypeException,
    InvalidActivityTypeException,
)


class ActivityType(str, Enum):
    COMMENT = "comment"
    STATUS_CHANGED = "status_changed"
    STAGE_CHANGED = "stage_changed"
    TASK_CREATED = "task_created"
    SYSTEM = "system"


@dataclass(frozen=True)
class ActivityTypeValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyActivityTypeException()

        try:
            ActivityType(self.value)
        except ValueError:
            raise InvalidActivityTypeException(activity_type=str(self.value))

    def as_generic_type(self) -> ActivityType:
        return ActivityType(self.value)


@dataclass(frozen=True)
class ActivityPayloadValueObject(BaseValueObject):
    value: dict[str, Any]

    def validate(self):
        if not isinstance(self.value, dict):
            raise ValueError("Activity payload must be a dictionary")

    def as_generic_type(self) -> dict[str, Any]:
        return self.value
