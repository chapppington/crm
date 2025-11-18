from dataclasses import dataclass
from uuid import UUID

from domain.organization.entities import OrganizationEntity
from domain.organization.exceptions.organization import OrganizationNotFoundException
from domain.organization.interfaces.repositories import BaseOrganizationRepository
from domain.organization.value_objects.organization import OrganizationNameValueObject


@dataclass
class OrganizationService:
    organization_repository: BaseOrganizationRepository

    async def create_organization(self, name: str) -> OrganizationEntity:
        organization = OrganizationEntity(
            name=OrganizationNameValueObject(name),
        )
        await self.organization_repository.add(organization)
        return organization

    async def get_organization_by_id(
        self,
        organization_id: UUID,
    ) -> OrganizationEntity:
        organization = await self.organization_repository.get_by_id(organization_id)
        if not organization:
            raise OrganizationNotFoundException(organization_id=organization_id)
        return organization
