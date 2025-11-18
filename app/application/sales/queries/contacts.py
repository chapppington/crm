from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.sales.entities import ContactEntity
from domain.sales.filters import ContactFilters
from domain.sales.services import ContactService


@dataclass(frozen=True)
class GetContactByIdQuery(BaseQuery):
    contact_id: UUID


@dataclass(frozen=True)
class GetContactsQuery(BaseQuery):
    filters: ContactFilters


@dataclass(frozen=True)
class GetContactByIdQueryHandler(
    BaseQueryHandler[GetContactByIdQuery, ContactEntity],
):
    contact_service: ContactService

    async def handle(
        self,
        query: GetContactByIdQuery,
    ) -> ContactEntity:
        return await self.contact_service.get_contact_by_id(
            contact_id=query.contact_id,
        )


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
        contacts = await self.contact_service.get_contact_list(query.filters)
        count = await self.contact_service.get_contact_count(query.filters)
        return contacts, count
