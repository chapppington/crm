from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities import TaskEntity
from domain.sales.interfaces.repositories.task import BaseTaskRepository


@dataclass
class DummyInMemoryTaskRepository(BaseTaskRepository):
    _saved_tasks: list[TaskEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    async def add(self, task: TaskEntity) -> None:
        self._saved_tasks.append(task)

    async def get_by_id(self, task_id: UUID) -> TaskEntity | None:
        try:
            return next(task for task in self._saved_tasks if task.oid == task_id)
        except StopIteration:
            return None

    async def update(self, task: TaskEntity) -> None:
        for i, saved_task in enumerate(self._saved_tasks):
            if saved_task.oid == task.oid:
                self._saved_tasks[i] = task
                return
