from dataclasses import dataclass
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organizations.entities import OrganizationMemberEntity
from domain.organizations.services import MemberService


@dataclass(frozen=True)
class AddMemberCommand(BaseCommand):
    organization_id: UUID
    user_id: UUID
    role: str


@dataclass(frozen=True)
class AddMemberCommandHandler(
    BaseCommandHandler[AddMemberCommand, OrganizationMemberEntity],
):
    member_service: MemberService

    async def handle(self, command: AddMemberCommand) -> OrganizationMemberEntity:
        result = await self.member_service.add_member(
            organization_id=command.organization_id,
            user_id=command.user_id,
            role=command.role,
        )
        return result
