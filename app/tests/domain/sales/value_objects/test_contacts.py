import pytest

from domain.sales.exceptions.sales import (
    EmptyContactNameException,
    EmptyContactPhoneException,
    InvalidContactEmailException,
    InvalidContactPhoneException,
)
from domain.sales.value_objects.contacts import (
    ContactEmailValueObject,
    ContactNameValueObject,
    ContactPhoneValueObject,
)


@pytest.mark.parametrize(
    "name_value,expected",
    [
        ("John Doe", "John Doe"),
        ("A" * 255, "A" * 255),
        ("Jane Smith", "Jane Smith"),
    ],
)
def test_contact_name_valid(name_value, expected):
    name = ContactNameValueObject(name_value)
    assert name.as_generic_type() == expected
    assert len(name.as_generic_type()) == len(expected)


@pytest.mark.parametrize(
    "name_value",
    [
        "",
        "A" * 256,
    ],
)
def test_contact_name_invalid(name_value):
    with pytest.raises(EmptyContactNameException):
        ContactNameValueObject(name_value)


@pytest.mark.parametrize(
    "email_value,expected",
    [
        ("test@example.com", "test@example.com"),
        ("user.name@domain.co.uk", "user.name@domain.co.uk"),
        (None, None),
    ],
)
def test_contact_email_valid(email_value, expected):
    email = ContactEmailValueObject(email_value)
    assert email.as_generic_type() == expected


@pytest.mark.parametrize(
    "email_value",
    [
        "invalid-email",
        "test@",
        "test@example",
        "@example.com",
    ],
)
def test_contact_email_invalid(email_value):
    with pytest.raises(InvalidContactEmailException):
        ContactEmailValueObject(email_value)


@pytest.mark.parametrize(
    "phone_value,expected",
    [
        ("+1234567890", "+1234567890"),
        ("+7 (495) 123-45-67", "+7 (495) 123-45-67"),
        (None, None),
    ],
)
def test_contact_phone_valid(phone_value, expected):
    phone = ContactPhoneValueObject(phone_value)
    assert phone.as_generic_type() == expected


@pytest.mark.parametrize(
    "phone_value,exception",
    [
        ("", EmptyContactPhoneException),
        ("123", InvalidContactPhoneException),
        ("1" * 20, InvalidContactPhoneException),
        ("abc", InvalidContactPhoneException),
    ],
)
def test_contact_phone_invalid(phone_value, exception):
    with pytest.raises(exception):
        ContactPhoneValueObject(phone_value)
