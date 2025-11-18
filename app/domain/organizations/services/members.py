from dataclasses import dataclass
from uuid import UUID

from domain.organizations.entities import (
    OrganizationEntity,
    OrganizationMemberEntity,
)
from domain.organizations.exceptions.members import (
    OrganizationMemberAlreadyExistsException,
    UserNotMemberOfOrganizationException,
)
from domain.organizations.interfaces.repositories import BaseOrganizationMemberRepository
from domain.organizations.value_objects.members import OrganizationMemberRoleValueObject


@dataclass
class MemberService:
    member_repository: BaseOrganizationMemberRepository

    async def add_member(
        self,
        organization_id: UUID,
        user_id: UUID,
        role: str,
    ) -> OrganizationMemberEntity:
        existing_member = await self.member_repository.get_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if existing_member:
            raise OrganizationMemberAlreadyExistsException(
                organization_id=organization_id,
                user_id=user_id,
            )

        member = OrganizationMemberEntity(
            organization_id=organization_id,
            user_id=user_id,
            role=OrganizationMemberRoleValueObject(role),
        )
        await self.member_repository.add(member)
        return member

    async def get_member_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMemberEntity:
        member = await self.member_repository.get_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if not member:
            raise UserNotMemberOfOrganizationException(
                user_id=user_id,
                organization_id=organization_id,
            )
        return member

    async def get_user_organizations(
        self,
        user_id: UUID,
    ) -> tuple[list[OrganizationMemberEntity], dict[UUID, OrganizationEntity]]:
        return await self.member_repository.get_by_user(user_id)
