from dataclasses import dataclass

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organizations.entities import OrganizationEntity
from domain.organizations.services import OrganizationService


@dataclass(frozen=True)
class CreateOrganizationCommand(BaseCommand):
    name: str


@dataclass(frozen=True)
class CreateOrganizationCommandHandler(
    BaseCommandHandler[CreateOrganizationCommand, OrganizationEntity],
):
    organization_service: OrganizationService

    async def handle(self, command: CreateOrganizationCommand) -> OrganizationEntity:
        result = await self.organization_service.create_organization(
            name=command.name,
        )
        return result
