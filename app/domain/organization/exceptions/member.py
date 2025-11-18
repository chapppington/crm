from dataclasses import dataclass
from uuid import UUID

from domain.organization.exceptions.organization import OrganizationException


@dataclass(eq=False)
class EmptyOrganizationMemberRoleException(OrganizationException):
    @property
    def message(self) -> str:
        return "Organization member role is empty"


@dataclass(eq=False)
class InvalidOrganizationMemberRoleException(OrganizationException):
    role: str

    @property
    def message(self) -> str:
        return f"Invalid organization member role: {self.role}"


@dataclass(eq=False)
class OrganizationMemberNotFoundException(OrganizationException):
    member_id: UUID

    @property
    def message(self) -> str:
        return f"Organization member with id {self.member_id} not found"


@dataclass(eq=False)
class OrganizationMemberAlreadyExistsException(OrganizationException):
    organization_id: UUID
    user_id: UUID

    @property
    def message(self) -> str:
        return f"User {self.user_id} is already a member of organization {self.organization_id}"


@dataclass(eq=False)
class UserNotMemberOfOrganizationException(OrganizationException):
    user_id: UUID
    organization_id: UUID

    @property
    def message(self) -> str:
        return f"User {self.user_id} is not a member of organization {self.organization_id}"
