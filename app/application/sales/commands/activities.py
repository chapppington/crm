from dataclasses import dataclass
from typing import Any
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.sales.entities import ActivityEntity
from domain.sales.services import ActivityService


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

    async def handle(
        self,
        command: CreateCommentActivityCommand,
    ) -> ActivityEntity:
        result = await self.activity_service.create_comment_activity(
            deal_id=command.deal_id,
            text=command.text,
            author_user_id=command.author_user_id,
        )
        return result
