from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
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
class GetActivitiesByDealIdQuery(BaseQuery):
    deal_id: UUID
    organization_id: UUID
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetActivitiesByDealIdQueryHandler(
    BaseQueryHandler[
        GetActivitiesByDealIdQuery,
        list[ActivityEntity],
    ],
):
    activity_service: ActivityService
    deal_service: DealService

    async def handle(
        self,
        query: GetActivitiesByDealIdQuery,
    ) -> list[ActivityEntity]:
        # Получаем deal для проверки прав
        deal = await self.deal_service.get_deal_by_id(query.deal_id)

        # Проверка принадлежности к организации
        if deal.organization_id != query.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Deal",
                resource_id=query.deal_id,
                organization_id=query.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(query.user_role)
        if role == OrganizationMemberRole.MEMBER and deal.owner_user_id != query.user_id:
            raise AccessDeniedException(
                resource_type="Activity",
                resource_id=query.deal_id,
                user_id=query.user_id,
            )

        return await self.activity_service.get_activities_by_deal_id(
            deal_id=query.deal_id,
        )
