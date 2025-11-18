from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities.contacts import ContactEntity
from domain.sales.filters.contacts import ContactFilters
from domain.sales.interfaces.repositories.contacts import BaseContactRepository


@dataclass
class DummyInMemoryContactRepository(BaseContactRepository):
    _saved_contacts: list[ContactEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    def _filter_items(self, items: list[ContactEntity], filters: ContactFilters) -> list[ContactEntity]:
        result = list(items)

        if filters.organization_id:
            result = [c for c in result if c.organization_id == filters.organization_id]
        if filters.owner_id:
            result = [c for c in result if c.owner_user_id == filters.owner_id]
        if filters.id:
            result = [c for c in result if c.oid == filters.id]
        if filters.ids:
            result = [c for c in result if c.oid in filters.ids]
        if filters.name:
            name_lower = filters.name.lower()
            result = [c for c in result if name_lower in c.name.as_generic_type().lower()]
        if filters.email:
            email_lower = filters.email.lower()
            result = [
                c for c in result if c.email.as_generic_type() and email_lower in c.email.as_generic_type().lower()
            ]
        if filters.phone:
            phone_lower = filters.phone.lower()
            result = [
                c for c in result if c.phone.as_generic_type() and phone_lower in c.phone.as_generic_type().lower()
            ]
        if filters.search:
            search_lower = filters.search.lower()
            result = [
                c
                for c in result
                if search_lower in c.name.as_generic_type().lower()
                or (c.email.as_generic_type() and search_lower in c.email.as_generic_type().lower())
                or (c.phone.as_generic_type() and search_lower in c.phone.as_generic_type().lower())
            ]
        if filters.created_at_from:
            result = [c for c in result if c.created_at >= filters.created_at_from]
        if filters.created_at_to:
            result = [c for c in result if c.created_at <= filters.created_at_to]

        return result

    async def add(self, contact: ContactEntity) -> None:
        self._saved_contacts.append(contact)

    async def get_by_id(self, contact_id: UUID) -> ContactEntity | None:
        try:
            return next(contact for contact in self._saved_contacts if contact.oid == contact_id)
        except StopIteration:
            return None

    async def delete(self, contact_id: UUID) -> None:
        self._saved_contacts = [contact for contact in self._saved_contacts if contact.oid != contact_id]

    async def get_list(
        self,
        filters: ContactFilters,
    ) -> Iterable[ContactEntity]:
        result = self._filter_items(self._saved_contacts, filters)

        offset = (filters.page - 1) * filters.page_size
        limit = filters.page_size

        return result[offset : offset + limit]

    async def get_count(
        self,
        filters: ContactFilters,
    ) -> int:
        result = self._filter_items(self._saved_contacts, filters)
        return len(result)
