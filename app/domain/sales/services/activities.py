from dataclasses import dataclass
from typing import Any
from uuid import UUID

from domain.sales.entities import ActivityEntity
from domain.sales.interfaces.repositories import BaseActivityRepository
from domain.sales.value_objects.activities import (
    ActivityPayloadValueObject,
    ActivityType,
    ActivityTypeValueObject,
)


@dataclass
class ActivityService:
    activity_repository: BaseActivityRepository

    async def create_activity(
        self,
        deal_id: UUID,
        activity_type: str,
        payload: dict[str, Any],
        author_user_id: UUID | None = None,
    ) -> ActivityEntity:
        activity = ActivityEntity(
            deal_id=deal_id,
            author_user_id=author_user_id,
            type=ActivityTypeValueObject(activity_type),
            payload=ActivityPayloadValueObject(payload),
        )
        await self.activity_repository.add(activity)
        return activity

    async def create_status_changed_activity(
        self,
        deal_id: UUID,
        old_status: str,
        new_status: str,
    ) -> ActivityEntity:
        return await self.create_activity(
            deal_id=deal_id,
            activity_type=ActivityType.STATUS_CHANGED.value,
            payload={
                "old_status": old_status,
                "new_status": new_status,
            },
            author_user_id=None,
        )

    async def create_stage_changed_activity(
        self,
        deal_id: UUID,
        old_stage: str,
        new_stage: str,
    ) -> ActivityEntity:
        return await self.create_activity(
            deal_id=deal_id,
            activity_type=ActivityType.STAGE_CHANGED.value,
            payload={
                "old_stage": old_stage,
                "new_stage": new_stage,
            },
            author_user_id=None,
        )

    async def create_task_created_activity(
        self,
        deal_id: UUID,
        task_id: UUID,
    ) -> ActivityEntity:
        return await self.create_activity(
            deal_id=deal_id,
            activity_type=ActivityType.TASK_CREATED.value,
            payload={
                "task_id": str(task_id),
            },
            author_user_id=None,
        )

    async def create_comment_activity(
        self,
        deal_id: UUID,
        text: str,
        author_user_id: UUID,
    ) -> ActivityEntity:
        return await self.create_activity(
            deal_id=deal_id,
            activity_type=ActivityType.COMMENT.value,
            payload={
                "text": text,
            },
            author_user_id=author_user_id,
        )

    async def get_activities_by_deal_id(
        self,
        deal_id: UUID,
    ) -> list[ActivityEntity]:
        return await self.activity_repository.get_by_deal_id(deal_id)
