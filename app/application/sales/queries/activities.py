from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.sales.entities import ActivityEntity
from domain.sales.services import ActivityService


@dataclass(frozen=True)
class GetActivitiesByDealIdQuery(BaseQuery):
    deal_id: UUID


@dataclass(frozen=True)
class GetActivitiesByDealIdQueryHandler(
    BaseQueryHandler[
        GetActivitiesByDealIdQuery,
        list[ActivityEntity],
    ],
):
    activity_service: ActivityService

    async def handle(
        self,
        query: GetActivitiesByDealIdQuery,
    ) -> list[ActivityEntity]:
        return await self.activity_service.get_activities_by_deal_id(
            deal_id=query.deal_id,
        )
