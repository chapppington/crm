from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities.tasks import TaskEntity
from domain.sales.filters.tasks import TaskFilters
from domain.sales.interfaces.repositories.tasks import BaseTaskRepository


@dataclass
class DummyInMemoryTaskRepository(BaseTaskRepository):
    _saved_tasks: list[TaskEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    def _filter_items(self, items: list[TaskEntity], filters: TaskFilters) -> list[TaskEntity]:
        result = list(items)

        if filters.deal_id:
            result = [t for t in result if t.deal_id == filters.deal_id]
        if filters.id:
            result = [t for t in result if t.oid == filters.id]
        if filters.ids:
            result = [t for t in result if t.oid in filters.ids]
        if filters.only_open is not None:
            if filters.only_open:
                result = [t for t in result if not t.is_done]
        if filters.is_done is not None:
            result = [t for t in result if t.is_done == filters.is_done]
        if filters.due_before:
            result = [
                t for t in result if t.due_date.as_generic_type() and t.due_date.as_generic_type() <= filters.due_before
            ]
        if filters.due_after:
            result = [
                t for t in result if t.due_date.as_generic_type() and t.due_date.as_generic_type() >= filters.due_after
            ]
        if filters.search:
            search_lower = filters.search.lower()
            result = [
                t
                for t in result
                if search_lower in t.title.as_generic_type().lower()
                or (t.description.as_generic_type() and search_lower in t.description.as_generic_type().lower())
            ]
        if filters.created_at_from:
            result = [t for t in result if t.created_at >= filters.created_at_from]
        if filters.created_at_to:
            result = [t for t in result if t.created_at <= filters.created_at_to]

        return result

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

    async def get_list(
        self,
        filters: TaskFilters,
    ) -> Iterable[TaskEntity]:
        result = self._filter_items(self._saved_tasks, filters)

        offset = (filters.page - 1) * filters.page_size
        limit = filters.page_size

        return result[offset : offset + limit]

    async def get_count(
        self,
        filters: TaskFilters,
    ) -> int:
        result = self._filter_items(self._saved_tasks, filters)
        return len(result)
