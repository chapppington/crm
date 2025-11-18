from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.sales.entities import TaskEntity
from domain.sales.filters import TaskFilters
from domain.sales.services import TaskService


@dataclass(frozen=True)
class GetTaskByIdQuery(BaseQuery):
    task_id: UUID


@dataclass(frozen=True)
class GetTasksQuery(BaseQuery):
    filters: TaskFilters


@dataclass(frozen=True)
class GetTaskByIdQueryHandler(
    BaseQueryHandler[GetTaskByIdQuery, TaskEntity],
):
    task_service: TaskService

    async def handle(
        self,
        query: GetTaskByIdQuery,
    ) -> TaskEntity:
        return await self.task_service.get_task_by_id(
            task_id=query.task_id,
        )


@dataclass(frozen=True)
class GetTasksQueryHandler(
    BaseQueryHandler[
        GetTasksQuery,
        tuple[Iterable[TaskEntity], int],
    ],
):
    task_service: TaskService

    async def handle(
        self,
        query: GetTasksQuery,
    ) -> tuple[Iterable[TaskEntity], int]:
        tasks = await self.task_service.get_task_list(query.filters)
        count = await self.task_service.get_task_count(query.filters)
        return tasks, count
