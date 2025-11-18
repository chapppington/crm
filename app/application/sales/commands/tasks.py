from dataclasses import dataclass
from datetime import date
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.sales.entities import TaskEntity
from domain.sales.services import (
    ActivityService,
    TaskService,
)


@dataclass(frozen=True)
class CreateTaskCommand(BaseCommand):
    deal_id: UUID
    title: str
    description: str | None = None
    due_date: date | None = None
    user_id: UUID | None = None
    is_deal_owner: bool = False


@dataclass(frozen=True)
class UpdateTaskCommand(BaseCommand):
    task_id: UUID
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

    async def handle(self, command: CreateTaskCommand) -> TaskEntity:
        result = await self.task_service.create_task(
            deal_id=command.deal_id,
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            user_id=command.user_id,
            is_deal_owner=command.is_deal_owner,
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

    async def handle(self, command: UpdateTaskCommand) -> TaskEntity:
        result = await self.task_service.update_task(
            task_id=command.task_id,
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            is_done=command.is_done,
        )
        return result
