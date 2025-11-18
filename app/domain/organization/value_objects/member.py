from dataclasses import dataclass
from enum import Enum

from domain.base.value_object import BaseValueObject
from domain.organization.exceptions.member import (
    EmptyOrganizationMemberRoleException,
    InvalidOrganizationMemberRoleException,
)


class OrganizationMemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


@dataclass(frozen=True)
class OrganizationMemberRoleValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyOrganizationMemberRoleException()

        try:
            OrganizationMemberRole(self.value)
        except ValueError:
            raise InvalidOrganizationMemberRoleException(role=str(self.value))

    def as_generic_type(self) -> OrganizationMemberRole:
        return OrganizationMemberRole(self.value)
