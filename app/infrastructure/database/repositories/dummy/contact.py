from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities import ContactEntity
from domain.sales.interfaces.repositories.contact import BaseContactRepository


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
