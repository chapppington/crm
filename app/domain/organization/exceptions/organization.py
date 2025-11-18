from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import DomainException


@dataclass(eq=False)
class OrganizationException(DomainException):
    @property
    def message(self) -> str:
        return "Organization exception occurred"


@dataclass(eq=False)
class EmptyOrganizationNameException(OrganizationException):
    @property
    def message(self) -> str:
        return "Organization name is empty"


@dataclass(eq=False)
class OrganizationNotFoundException(OrganizationException):
    organization_id: UUID

    @property
    def message(self) -> str:
        return f"Organization with id {self.organization_id} not found"
