from infrastructure.database.models.organizations.organization import OrganizationModel

from domain.organizations.entities.organizations import OrganizationEntity
from domain.organizations.value_objects.organizations import OrganizationNameValueObject


def organization_entity_to_model(entity: OrganizationEntity) -> OrganizationModel:
    return OrganizationModel(
        oid=entity.oid,
        name=entity.name.as_generic_type(),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def organization_model_to_entity(model: OrganizationModel) -> OrganizationEntity:
    return OrganizationEntity(
        oid=model.oid,
        name=OrganizationNameValueObject(value=model.name),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
