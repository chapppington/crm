from dataclasses import dataclass
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import ContactEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    ResourceNotFoundInOrganizationException,
)
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
    organization_id: UUID
    user_id: UUID
    user_role: str


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
        # Сначала получаем контакт для проверки прав
        contact = await self.contact_service.get_contact_by_id(command.contact_id)

        # Проверка принадлежности к организации
        if contact.organization_id != command.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Contact",
                resource_id=command.contact_id,
                organization_id=command.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(command.user_role)
        if role == OrganizationMemberRole.MEMBER and contact.owner_user_id != command.user_id:
            raise AccessDeniedException(
                resource_type="Contact",
                resource_id=command.contact_id,
                user_id=command.user_id,
            )

        await self.contact_service.delete_contact(
            contact_id=command.contact_id,
        )
