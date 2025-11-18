from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.organizations.entities import (
    OrganizationEntity,
    OrganizationMemberEntity,
)
from domain.organizations.interfaces.repositories.members import BaseOrganizationMemberRepository


@dataclass
class DummyInMemoryOrganizationMemberRepository(BaseOrganizationMemberRepository):
    _saved_members: list[OrganizationMemberEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    async def add(self, member: OrganizationMemberEntity) -> None:
        self._saved_members.append(member)

    async def get_by_id(
        self,
        member_id: UUID,
    ) -> OrganizationMemberEntity | None:
        try:
            return next(member for member in self._saved_members if member.oid == member_id)
        except StopIteration:
            return None

    async def get_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMemberEntity | None:
        try:
            return next(
                member
                for member in self._saved_members
                if member.organization_id == organization_id and member.user_id == user_id
            )
        except StopIteration:
            return None

    async def get_by_user(
        self,
        user_id: UUID,
    ) -> tuple[list[OrganizationMemberEntity], dict[UUID, OrganizationEntity]]:
        members = [member for member in self._saved_members if member.user_id == user_id]
        organizations_map: dict[UUID, OrganizationEntity] = {}
        return members, organizations_map
