from infrastructure.database.models.sales.contact import ContactModel

from domain.sales.entities.contacts import ContactEntity
from domain.sales.value_objects.contacts import (
    ContactEmailValueObject,
    ContactNameValueObject,
    ContactPhoneValueObject,
)


def contact_entity_to_model(entity: ContactEntity) -> ContactModel:
    return ContactModel(
        oid=entity.oid,
        organization_id=entity.organization_id,
        owner_id=entity.owner_user_id,
        name=entity.name.as_generic_type(),
        email=entity.email.as_generic_type(),
        phone=entity.phone.as_generic_type(),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def contact_model_to_entity(model: ContactModel) -> ContactEntity:
    return ContactEntity(
        oid=model.oid,
        organization_id=model.organization_id,
        owner_user_id=model.owner_id,
        name=ContactNameValueObject(value=model.name),
        email=ContactEmailValueObject(value=model.email),
        phone=ContactPhoneValueObject(value=model.phone),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
