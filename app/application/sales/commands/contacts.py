from dataclasses import dataclass
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.sales.entities import ContactEntity
from domain.sales.services import ContactService


@dataclass(frozen=True)
class CreateContactCommand(BaseCommand):
    organization_id: UUID
    owner_user_id: UUID
    name: str
    email: str | None = None
    phone: str | None = None


@dataclass(frozen=True)
class DeleteContactCommand(BaseCommand):
    contact_id: UUID


@dataclass(frozen=True)
class CreateContactCommandHandler(
    BaseCommandHandler[CreateContactCommand, ContactEntity],
):
    contact_service: ContactService

    async def handle(self, command: CreateContactCommand) -> ContactEntity:
        result = await self.contact_service.create_contact(
            organization_id=command.organization_id,
            owner_user_id=command.owner_user_id,
            name=command.name,
            email=command.email,
            phone=command.phone,
        )
        return result


@dataclass(frozen=True)
class DeleteContactCommandHandler(
    BaseCommandHandler[DeleteContactCommand, None],
):
    contact_service: ContactService

    async def handle(self, command: DeleteContactCommand) -> None:
        await self.contact_service.delete_contact(
            contact_id=command.contact_id,
        )
