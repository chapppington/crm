from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.sales.entities import TaskEntity


class BaseTaskRepository(ABC):
    @abstractmethod
    async def add(self, task: TaskEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> TaskEntity | None: ...

    @abstractmethod
    async def update(self, task: TaskEntity) -> None: ...
