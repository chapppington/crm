from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import ActivityEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    ResourceNotFoundInOrganizationException,
)
from domain.sales.services import (
    ActivityService,
    DealService,
)


@dataclass(frozen=True)
class CreateActivityCommand(BaseCommand):
    deal_id: UUID
    activity_type: str
    payload: dict[str, Any]
    author_user_id: UUID | None = None


@dataclass(frozen=True)
class CreateCommentActivityCommand(BaseCommand):
    deal_id: UUID
    text: str
    author_user_id: UUID
    organization_id: UUID
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class CreateActivityCommandHandler(
    BaseCommandHandler[CreateActivityCommand, ActivityEntity],
):
    activity_service: ActivityService

    async def handle(self, command: CreateActivityCommand) -> ActivityEntity:
        result = await self.activity_service.create_activity(
            deal_id=command.deal_id,
            activity_type=command.activity_type,
            payload=command.payload,
            author_user_id=command.author_user_id,
        )
        return result


@dataclass(frozen=True)
class CreateCommentActivityCommandHandler(
    BaseCommandHandler[CreateCommentActivityCommand, ActivityEntity],
):
    activity_service: ActivityService
    deal_service: DealService

    async def handle(
        self,
        command: CreateCommentActivityCommand,
    ) -> ActivityEntity:
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
        if role == OrganizationMemberRole.MEMBER and deal.owner_user_id != command.user_id:
            raise AccessDeniedException(
                resource_type="Activity",
                resource_id=command.deal_id,
                user_id=command.user_id,
            )

        result = await self.activity_service.create_comment_activity(
            deal_id=command.deal_id,
            text=command.text,
            author_user_id=command.author_user_id,
        )
        return result
