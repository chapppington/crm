import re
from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.sales.exceptions.sales import (
    EmptyContactNameException,
    EmptyContactPhoneException,
    InvalidContactEmailException,
    InvalidContactPhoneException,
)


@dataclass(frozen=True)
class ContactNameValueObject(BaseValueObject):
    value: str
    MAX_LENGTH = 255

    def validate(self):
        if not self.value:
            raise EmptyContactNameException()

        if len(self.value) > self.MAX_LENGTH:
            raise EmptyContactNameException()

    def as_generic_type(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class ContactEmailValueObject(BaseValueObject):
    value: str | None = None

    def validate(self):
        if self.value is None:
            return

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise InvalidContactEmailException(email=self.value)

    def as_generic_type(self) -> str | None:
        return self.value


@dataclass(frozen=True)
class ContactPhoneValueObject(BaseValueObject):
    value: str | None = None

    def validate(self):
        if self.value is None:
            return

        if not self.value:
            raise EmptyContactPhoneException()

        digits_only = re.sub(r"[^\d]", "", self.value)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise InvalidContactPhoneException(phone=self.value)

        phone_pattern = r"^[\+]?[\d\s\-\(\)]{10,}$"
        if not re.match(phone_pattern, self.value):
            raise InvalidContactPhoneException(phone=self.value)

    def as_generic_type(self) -> str | None:
        return self.value
