import pytest

from domain.organizations.exceptions.organizations import EmptyOrganizationNameException
from domain.organizations.value_objects.organizations import OrganizationNameValueObject


@pytest.mark.parametrize(
    "name_value,expected",
    [
        ("Test Organization", "Test Organization"),
        ("  Test  ", "  Test  "),
        ("Acme Inc", "Acme Inc"),
    ],
)
def test_organization_name_valid(name_value, expected):
    name = OrganizationNameValueObject(name_value)
    assert name.as_generic_type() == expected


def test_organization_name_empty():
    with pytest.raises(EmptyOrganizationNameException):
        OrganizationNameValueObject("")
