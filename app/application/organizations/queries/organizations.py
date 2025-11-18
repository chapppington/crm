from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organizations.entities import OrganizationEntity
from domain.organizations.services import OrganizationService


@dataclass(frozen=True)
class GetOrganizationByIdQuery(BaseQuery):
    organization_id: UUID


@dataclass(frozen=True)
class GetOrganizationByIdQueryHandler(
    BaseQueryHandler[GetOrganizationByIdQuery, OrganizationEntity],
):
    organization_service: OrganizationService

    async def handle(
        self,
        query: GetOrganizationByIdQuery,
    ) -> OrganizationEntity:
        return await self.organization_service.get_organization_by_id(
            query.organization_id,
        )
