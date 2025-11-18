from dataclasses import dataclass
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.sales.value_objects.contact import (
    ContactEmailValueObject,
    ContactNameValueObject,
    ContactPhoneValueObject,
)


@dataclass(eq=False)
class ContactEntity(BaseEntity):
    organization_id: UUID
    owner_user_id: UUID
    name: ContactNameValueObject
    email: ContactEmailValueObject
    phone: ContactPhoneValueObject
