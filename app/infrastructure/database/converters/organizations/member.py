from infrastructure.database.models.organizations.member import OrganizationMemberModel

from domain.organizations.entities.members import OrganizationMemberEntity
from domain.organizations.value_objects.members import OrganizationMemberRoleValueObject


def organization_member_entity_to_model(entity: OrganizationMemberEntity) -> OrganizationMemberModel:
    return OrganizationMemberModel(
        oid=entity.oid,
        organization_id=entity.organization_id,
        user_id=entity.user_id,
        role=entity.role.as_generic_type().value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def organization_member_model_to_entity(model: OrganizationMemberModel) -> OrganizationMemberEntity:
    return OrganizationMemberEntity(
        oid=model.oid,
        organization_id=model.organization_id,
        user_id=model.user_id,
        role=OrganizationMemberRoleValueObject(value=model.role),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
