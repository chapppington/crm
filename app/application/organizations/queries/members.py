from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organizations.entities import (
    OrganizationEntity,
    OrganizationMemberEntity,
)
from domain.organizations.services import MemberService


@dataclass(frozen=True)
class GetMemberByOrganizationAndUserQuery(BaseQuery):
    organization_id: UUID
    user_id: UUID


@dataclass(frozen=True)
class GetUserOrganizationsQuery(BaseQuery):
    user_id: UUID


@dataclass(frozen=True)
class GetMemberByOrganizationAndUserQueryHandler(
    BaseQueryHandler[
        GetMemberByOrganizationAndUserQuery,
        OrganizationMemberEntity,
    ],
):
    member_service: MemberService

    async def handle(
        self,
        query: GetMemberByOrganizationAndUserQuery,
    ) -> OrganizationMemberEntity:
        return await self.member_service.get_member_by_organization_and_user(
            organization_id=query.organization_id,
            user_id=query.user_id,
        )


@dataclass(frozen=True)
class GetUserOrganizationsQueryHandler(
    BaseQueryHandler[
        GetUserOrganizationsQuery,
        tuple[list[OrganizationMemberEntity], dict[UUID, OrganizationEntity]],
    ],
):
    member_service: MemberService

    async def handle(
        self,
        query: GetUserOrganizationsQuery,
    ) -> tuple[list[OrganizationMemberEntity], dict[UUID, OrganizationEntity]]:
        return await self.member_service.get_user_organizations(
            user_id=query.user_id,
        )
