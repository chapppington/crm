from uuid import uuid4

from domain.organizations.entities import OrganizationEntity
from domain.organizations.value_objects.organizations import OrganizationNameValueObject


def test_organization_entity_creation():
    organization = OrganizationEntity(
        name=OrganizationNameValueObject("Test Org"),
    )

    assert organization.name.as_generic_type() == "Test Org"
    assert organization.oid is not None
    assert organization.created_at is not None
    assert organization.updated_at is not None


def test_organization_entity_equality():
    org_id = uuid4()
    name = OrganizationNameValueObject("Test Org")

    org1 = OrganizationEntity(oid=org_id, name=name)
    org2 = OrganizationEntity(oid=org_id, name=name)

    assert org1 == org2
    assert hash(org1) == hash(org2)
