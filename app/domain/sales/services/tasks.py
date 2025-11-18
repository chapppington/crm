from dataclasses import dataclass
from datetime import date
from uuid import UUID

from domain.sales.entities import TaskEntity
from domain.sales.exceptions.sales import (
    CannotCreateTaskForOtherUserDealException,
    DealNotFoundException,
    TaskNotFoundException,
)
from domain.sales.interfaces.repositories import (
    BaseDealRepository,
    BaseTaskRepository,
)
from domain.sales.value_objects.tasks import (
    TaskDescriptionValueObject,
    TaskDueDateValueObject,
    TaskTitleValueObject,
)


@dataclass
class TaskService:
    task_repository: BaseTaskRepository
    deal_repository: BaseDealRepository

    async def create_task(
        self,
        deal_id: UUID,
        title: str,
        description: str | None = None,
        due_date: date | None = None,
        user_id: UUID | None = None,
        is_deal_owner: bool = False,
    ) -> TaskEntity:
        deal = await self.deal_repository.get_by_id(deal_id)
        if not deal:
            raise DealNotFoundException(deal_id=deal_id)

        if user_id and not is_deal_owner:
            if deal.owner_user_id != user_id:
                raise CannotCreateTaskForOtherUserDealException(
                    deal_id=deal_id,
                    user_id=deal.owner_user_id,
                )

        task = TaskEntity(
            deal_id=deal_id,
            title=TaskTitleValueObject(title),
            description=TaskDescriptionValueObject(description),
            due_date=TaskDueDateValueObject(due_date),
            is_done=False,
        )
        await self.task_repository.add(task)
        return task

    async def get_task_by_id(
        self,
        task_id: UUID,
    ) -> TaskEntity:
        task = await self.task_repository.get_by_id(task_id)

        if not task:
            raise TaskNotFoundException(task_id=task_id)

        return task

    async def update_task(
        self,
        task_id: UUID,
        title: str | None = None,
        description: str | None = None,
        due_date: date | None = None,
        is_done: bool | None = None,
    ) -> TaskEntity:
        task = await self.get_task_by_id(task_id)

        if title is not None:
            task.title = TaskTitleValueObject(title)
        if description is not None:
            task.description = TaskDescriptionValueObject(description)
        if due_date is not None:
            task.due_date = TaskDueDateValueObject(due_date)
        if is_done is not None:
            task.is_done = is_done

        await self.task_repository.update(task)
        return task
