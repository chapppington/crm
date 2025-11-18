from dataclasses import dataclass
from datetime import date

from domain.base.value_object import BaseValueObject
from domain.sales.exceptions.sales import (
    EmptyTaskDescriptionException,
    EmptyTaskTitleException,
    InvalidTaskDueDateException,
)


@dataclass(frozen=True)
class TaskTitleValueObject(BaseValueObject):
    value: str
    MAX_LENGTH = 255

    def validate(self):
        if not self.value:
            raise EmptyTaskTitleException()

        if len(self.value) > self.MAX_LENGTH:
            raise EmptyTaskTitleException()

    def as_generic_type(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class TaskDescriptionValueObject(BaseValueObject):
    value: str | None = None

    def validate(self):
        if self.value is None:
            return

        if not self.value:
            raise EmptyTaskDescriptionException()

    def as_generic_type(self) -> str | None:
        return self.value


@dataclass(frozen=True)
class TaskDueDateValueObject(BaseValueObject):
    value: date | None = None

    def validate(self):
        if self.value is None:
            return

        today = date.today()
        if self.value < today:
            raise InvalidTaskDueDateException(due_date=self.value, today=today)

    def as_generic_type(self) -> date | None:
        return self.value
