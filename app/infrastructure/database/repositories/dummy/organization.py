from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.organization.entities import OrganizationEntity
from domain.organization.interfaces.repositories.organization import BaseOrganizationRepository


@dataclass
class DummyInMemoryOrganizationRepository(BaseOrganizationRepository):
    _saved_organizations: list[OrganizationEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    async def add(self, organization: OrganizationEntity) -> None:
        self._saved_organizations.append(organization)

    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None:
        try:
            return next(org for org in self._saved_organizations if org.oid == organization_id)
        except StopIteration:
            return None
