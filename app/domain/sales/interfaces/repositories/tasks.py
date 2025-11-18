from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from uuid import UUID

from domain.sales.entities import TaskEntity
from domain.sales.filters import TaskFilters


class BaseTaskRepository(ABC):
    @abstractmethod
    async def add(self, task: TaskEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> TaskEntity | None: ...

    @abstractmethod
    async def update(self, task: TaskEntity) -> None: ...

    @abstractmethod
    async def get_list(
        self,
        filters: TaskFilters,
    ) -> Iterable[TaskEntity]: ...

    @abstractmethod
    async def get_count(
        self,
        filters: TaskFilters,
    ) -> int: ...
