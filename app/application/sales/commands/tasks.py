from dataclasses import dataclass
from datetime import date
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import TaskEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    ResourceNotFoundInOrganizationException,
)
from domain.sales.services import (
    ActivityService,
    DealService,
    TaskService,
)


@dataclass(frozen=True)
class CreateTaskCommand(BaseCommand):
    deal_id: UUID
    title: str
    organization_id: UUID
    user_id: UUID
    user_role: str
    description: str | None = None
    due_date: date | None = None


@dataclass(frozen=True)
class UpdateTaskCommand(BaseCommand):
    task_id: UUID
    organization_id: UUID
    user_id: UUID
    user_role: str
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    is_done: bool | None = None


@dataclass(frozen=True)
class CreateTaskCommandHandler(
    BaseCommandHandler[CreateTaskCommand, TaskEntity],
):
    task_service: TaskService
    activity_service: ActivityService
    deal_service: DealService

    async def handle(self, command: CreateTaskCommand) -> TaskEntity:
        # Получаем deal для проверки прав
        deal = await self.deal_service.get_deal_by_id(command.deal_id)

        # Проверка принадлежности к организации
        if deal.organization_id != command.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Deal",
                resource_id=command.deal_id,
                organization_id=command.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(command.user_role)
        is_deal_owner = deal.owner_user_id == command.user_id

        if role == OrganizationMemberRole.MEMBER and not is_deal_owner:
            raise AccessDeniedException(
                resource_type="Task",
                resource_id=command.deal_id,
                user_id=command.user_id,
            )

        result = await self.task_service.create_task(
            deal_id=command.deal_id,
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            user_id=command.user_id,
            is_deal_owner=is_deal_owner,
        )

        await self.activity_service.create_task_created_activity(
            deal_id=command.deal_id,
            task_id=result.oid,
        )

        return result


@dataclass(frozen=True)
class UpdateTaskCommandHandler(
    BaseCommandHandler[UpdateTaskCommand, TaskEntity],
):
    task_service: TaskService
    deal_service: DealService

    async def handle(self, command: UpdateTaskCommand) -> TaskEntity:
        # Получаем task для проверки прав
        task = await self.task_service.get_task_by_id(command.task_id)

        # Получаем deal для проверки организации
        deal = await self.deal_service.get_deal_by_id(task.deal_id)

        # Проверка принадлежности к организации
        if deal.organization_id != command.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Task",
                resource_id=command.task_id,
                organization_id=command.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(command.user_role)
        if role == OrganizationMemberRole.MEMBER and deal.owner_user_id != command.user_id:
            raise AccessDeniedException(
                resource_type="Task",
                resource_id=command.task_id,
                user_id=command.user_id,
            )

        result = await self.task_service.update_task(
            task_id=command.task_id,
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            is_done=command.is_done,
        )
        return result
