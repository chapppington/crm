from dataclasses import dataclass
from uuid import UUID

from domain.sales.entities import ContactEntity
from domain.sales.exceptions.sales import (
    ContactHasActiveDealsException,
    ContactNotFoundException,
)
from domain.sales.interfaces.repositories import (
    BaseContactRepository,
    BaseDealRepository,
)
from domain.sales.value_objects.contact import (
    ContactEmailValueObject,
    ContactNameValueObject,
    ContactPhoneValueObject,
)


@dataclass
class ContactService:
    contact_repository: BaseContactRepository
    deal_repository: BaseDealRepository

    async def create_contact(
        self,
        organization_id: UUID,
        owner_user_id: UUID,
        name: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> ContactEntity:
        contact = ContactEntity(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=ContactNameValueObject(name),
            email=ContactEmailValueObject(email),
            phone=ContactPhoneValueObject(phone),
        )
        await self.contact_repository.add(contact)
        return contact

    async def get_contact_by_id(
        self,
        contact_id: UUID,
    ) -> ContactEntity:
        contact = await self.contact_repository.get_by_id(contact_id)

        if not contact:
            raise ContactNotFoundException(contact_id=contact_id)

        return contact

    async def delete_contact(
        self,
        contact_id: UUID,
    ) -> None:
        deals = await self.deal_repository.get_by_contact_id(contact_id)

        if deals:
            raise ContactHasActiveDealsException(contact_id=contact_id)

        await self.contact_repository.delete(contact_id)
