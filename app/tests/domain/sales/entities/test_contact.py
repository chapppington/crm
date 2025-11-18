from uuid import uuid4

from domain.sales.entities import ContactEntity
from domain.sales.value_objects.contact import (
    ContactEmailValueObject,
    ContactNameValueObject,
    ContactPhoneValueObject,
)


def test_contact_entity_creation():
    org_id = uuid4()
    user_id = uuid4()

    contact = ContactEntity(
        organization_id=org_id,
        owner_user_id=user_id,
        name=ContactNameValueObject("John Doe"),
        email=ContactEmailValueObject("john@example.com"),
        phone=ContactPhoneValueObject("+1234567890"),
    )

    assert contact.organization_id == org_id
    assert contact.owner_user_id == user_id
    assert contact.name.as_generic_type() == "John Doe"
    assert contact.email.as_generic_type() == "john@example.com"
    assert contact.phone.as_generic_type() == "+1234567890"
    assert contact.oid is not None
    assert contact.created_at is not None


def test_contact_entity_equality():
    contact_id = uuid4()
    org_id = uuid4()
    user_id = uuid4()

    contact1 = ContactEntity(
        oid=contact_id,
        organization_id=org_id,
        owner_user_id=user_id,
        name=ContactNameValueObject("John Doe"),
        email=ContactEmailValueObject("john@example.com"),
        phone=ContactPhoneValueObject("+1234567890"),
    )
    contact2 = ContactEntity(
        oid=contact_id,
        organization_id=org_id,
        owner_user_id=user_id,
        name=ContactNameValueObject("John Doe"),
        email=ContactEmailValueObject("john@example.com"),
        phone=ContactPhoneValueObject("+1234567890"),
    )

    assert contact1 == contact2
    assert hash(contact1) == hash(contact2)
