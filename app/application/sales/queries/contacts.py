from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import ContactEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    ResourceNotFoundInOrganizationException,
)
from domain.sales.filters import ContactFilters
from domain.sales.services import ContactService


@dataclass(frozen=True)
class GetContactByIdQuery(BaseQuery):
    contact_id: UUID
    organization_id: UUID
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetContactsQuery(BaseQuery):
    filters: ContactFilters
    user_id: UUID
    user_role: str
    owner_id: UUID | None = None


@dataclass(frozen=True)
class GetContactByIdQueryHandler(
    BaseQueryHandler[GetContactByIdQuery, ContactEntity],
):
    contact_service: ContactService

    async def handle(
        self,
        query: GetContactByIdQuery,
    ) -> ContactEntity:
        contact = await self.contact_service.get_contact_by_id(
            contact_id=query.contact_id,
        )

        # Проверка принадлежности к организации
        if contact.organization_id != query.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Contact",
                resource_id=query.contact_id,
                organization_id=query.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(query.user_role)
        if role == OrganizationMemberRole.MEMBER and contact.owner_user_id != query.user_id:
            raise AccessDeniedException(
                resource_type="Contact",
                resource_id=query.contact_id,
                user_id=query.user_id,
            )

        return contact


@dataclass(frozen=True)
class GetContactsQueryHandler(
    BaseQueryHandler[
        GetContactsQuery,
        tuple[Iterable[ContactEntity], int],
    ],
):
    contact_service: ContactService

    async def handle(
        self,
        query: GetContactsQuery,
    ) -> tuple[Iterable[ContactEntity], int]:
        role = OrganizationMemberRole(query.user_role)

        # Проверка прав на фильтрацию по owner_id
        if query.owner_id is not None and role == OrganizationMemberRole.MEMBER:
            raise AccessDeniedException(
                resource_type="Contact",
                resource_id=query.user_id,
                user_id=query.user_id,
            )

        # Для member автоматически фильтруем по его контактам, если owner_id не указан
        filters = query.filters
        if role == OrganizationMemberRole.MEMBER and filters.owner_id is None:
            filters = ContactFilters.model_validate(
                {**filters.model_dump(), "owner_id": query.user_id},
            )

        contacts = await self.contact_service.get_contact_list(filters)
        count = await self.contact_service.get_contact_count(filters)
        return contacts, count
