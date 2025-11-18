from uuid import uuid4

from domain.organization.entities import OrganizationMemberEntity
from domain.organization.value_objects.member import OrganizationMemberRoleValueObject


def test_member_entity_creation():
    org_id = uuid4()
    user_id = uuid4()

    member = OrganizationMemberEntity(
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationMemberRoleValueObject("owner"),
    )

    assert member.organization_id == org_id
    assert member.user_id == user_id
    assert member.role.as_generic_type().value == "owner"
    assert member.oid is not None
    assert member.created_at is not None


def test_member_entity_equality():
    member_id = uuid4()
    org_id = uuid4()
    user_id = uuid4()

    member1 = OrganizationMemberEntity(
        oid=member_id,
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationMemberRoleValueObject("admin"),
    )
    member2 = OrganizationMemberEntity(
        oid=member_id,
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationMemberRoleValueObject("admin"),
    )

    assert member1 == member2
    assert hash(member1) == hash(member2)
