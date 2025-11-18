from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities import ContactEntity
from domain.sales.filters import ContactFilters
from domain.sales.interfaces.repositories.contacts import BaseContactRepository


@dataclass
class DummyInMemoryContactRepository(BaseContactRepository):
    _saved_contacts: list[ContactEntity] = field(
        default_factory=list,
        kw_only=True,
    )

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
        result = list(self._saved_contacts)

        if filters.organization_id:
            result = [c for c in result if c.organization_id == filters.organization_id]
        if filters.owner_id:
            result = [c for c in result if c.owner_user_id == filters.owner_id]
        if filters.id:
            result = [c for c in result if c.oid == filters.id]
        if filters.ids:
            result = [c for c in result if c.oid in filters.ids]

        offset = (filters.page - 1) * filters.page_size
        limit = filters.page_size

        return result[offset : offset + limit]

    async def get_count(
        self,
        filters: ContactFilters,
    ) -> int:
        result = list(self._saved_contacts)

        if filters.organization_id:
            result = [c for c in result if c.organization_id == filters.organization_id]
        if filters.owner_id:
            result = [c for c in result if c.owner_user_id == filters.owner_id]
        if filters.id:
            result = [c for c in result if c.oid == filters.id]
        if filters.ids:
            result = [c for c in result if c.oid in filters.ids]

        return len(result)
