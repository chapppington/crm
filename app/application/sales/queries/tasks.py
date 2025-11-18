from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import TaskEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    ResourceNotFoundInOrganizationException,
)
from domain.sales.filters import TaskFilters
from domain.sales.services import (
    DealService,
    TaskService,
)


@dataclass(frozen=True)
class GetTaskByIdQuery(BaseQuery):
    task_id: UUID
    organization_id: UUID
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetTasksQuery(BaseQuery):
    filters: TaskFilters
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetTaskByIdQueryHandler(
    BaseQueryHandler[GetTaskByIdQuery, TaskEntity],
):
    task_service: TaskService
    deal_service: DealService

    async def handle(
        self,
        query: GetTaskByIdQuery,
    ) -> TaskEntity:
        task = await self.task_service.get_task_by_id(
            task_id=query.task_id,
        )

        # Получаем deal для проверки организации
        deal = await self.deal_service.get_deal_by_id(task.deal_id)

        # Проверка принадлежности к организации
        if deal.organization_id != query.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Task",
                resource_id=query.task_id,
                organization_id=query.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(query.user_role)
        if role == OrganizationMemberRole.MEMBER and deal.owner_user_id != query.user_id:
            raise AccessDeniedException(
                resource_type="Task",
                resource_id=query.task_id,
                user_id=query.user_id,
            )

        return task


@dataclass(frozen=True)
class GetTasksQueryHandler(
    BaseQueryHandler[
        GetTasksQuery,
        tuple[Iterable[TaskEntity], int],
    ],
):
    task_service: TaskService
    deal_service: DealService

    async def handle(
        self,
        query: GetTasksQuery,
    ) -> tuple[Iterable[TaskEntity], int]:
        # Для member автоматически фильтруем по его сделкам
        role = OrganizationMemberRole(query.user_role)
        filters = query.filters

        if role == OrganizationMemberRole.MEMBER and filters.deal_id is None:
            # Если member не указал deal_id, нужно фильтровать по его сделкам
            # Но это сложно сделать на уровне фильтров, поэтому просто проверяем доступ к каждой задаче
            # В реальности лучше добавить фильтр по owner_id в TaskFilters через deal
            pass

        tasks = await self.task_service.get_task_list(filters)
        count = await self.task_service.get_task_count(filters)

        # Фильтруем задачи по правам доступа для member
        if role == OrganizationMemberRole.MEMBER:
            filtered_tasks = []
            for task in tasks:
                deal = await self.deal_service.get_deal_by_id(task.deal_id)
                if deal.owner_user_id == query.user_id:
                    filtered_tasks.append(task)
            tasks = filtered_tasks
            count = len(filtered_tasks)

        return tasks, count
