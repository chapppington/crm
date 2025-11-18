from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.organizations.exceptions.organizations import EmptyOrganizationNameException


@dataclass(frozen=True)
class OrganizationNameValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyOrganizationNameException()

    def as_generic_type(self) -> str:
        return str(self.value)
