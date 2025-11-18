from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.organizations.organization import (
    organization_entity_to_model,
    organization_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.organizations.organization import OrganizationModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.organizations.entities.organizations import OrganizationEntity
from domain.organizations.interfaces.repositories.organizations import BaseOrganizationRepository


@dataclass
class SQLAlchemyOrganizationRepository(BaseOrganizationRepository):
    database: Database

    async def add(self, organization: OrganizationEntity) -> None:
        async with self.database.get_session() as session:
            org_model = organization_entity_to_model(organization)
            session.add(org_model)
            await session.commit()

    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(OrganizationModel)
                .where(OrganizationModel.oid == organization_id)
                .options(
                    selectinload(OrganizationModel.members),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return organization_model_to_entity(result) if result else None
