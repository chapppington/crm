import pytest

from domain.organizations.exceptions.members import (
    EmptyOrganizationMemberRoleException,
    InvalidOrganizationMemberRoleException,
)
from domain.organizations.value_objects.members import (
    OrganizationMemberRole,
    OrganizationMemberRoleValueObject,
)


@pytest.mark.parametrize(
    "role_value,expected_role",
    [
        ("owner", OrganizationMemberRole.OWNER),
        ("admin", OrganizationMemberRole.ADMIN),
        ("manager", OrganizationMemberRole.MANAGER),
        ("member", OrganizationMemberRole.MEMBER),
    ],
)
def test_member_role_valid(role_value, expected_role):
    role = OrganizationMemberRoleValueObject(role_value)
    assert role.as_generic_type() == expected_role


@pytest.mark.parametrize(
    "role_value,exception",
    [
        ("", EmptyOrganizationMemberRoleException),
        ("invalid_role", InvalidOrganizationMemberRoleException),
        ("admin_user", InvalidOrganizationMemberRoleException),
    ],
)
def test_member_role_invalid(role_value, exception):
    with pytest.raises(exception):
        OrganizationMemberRoleValueObject(role_value)
