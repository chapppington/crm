from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.organizations.member import (
    organization_member_entity_to_model,
    organization_member_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.organizations.member import OrganizationMemberModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.organizations.entities.members import OrganizationMemberEntity
from domain.organizations.interfaces.repositories.members import BaseOrganizationMemberRepository


@dataclass
class SQLAlchemyOrganizationMemberRepository(BaseOrganizationMemberRepository):
    database: Database

    async def add(self, member: OrganizationMemberEntity) -> None:
        async with self.database.get_session() as session:
            member_model = organization_member_entity_to_model(member)
            session.add(member_model)
            await session.commit()

    async def get_by_id(
        self,
        member_id: UUID,
    ) -> OrganizationMemberEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(OrganizationMemberModel)
                .where(OrganizationMemberModel.oid == member_id)
                .options(
                    selectinload(OrganizationMemberModel.organization),
                    selectinload(OrganizationMemberModel.user),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return organization_member_model_to_entity(result) if result else None

    async def get_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMemberEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(OrganizationMemberModel)
                .where(
                    OrganizationMemberModel.organization_id == organization_id,
                    OrganizationMemberModel.user_id == user_id,
                )
                .options(
                    selectinload(OrganizationMemberModel.organization),
                    selectinload(OrganizationMemberModel.user),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return organization_member_model_to_entity(result) if result else None

    async def get_by_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationMemberEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(OrganizationMemberModel)
                .where(OrganizationMemberModel.user_id == user_id)
                .options(
                    selectinload(OrganizationMemberModel.organization),
                    selectinload(OrganizationMemberModel.user),
                )
            )
            res = await session.execute(stmt)
            results = res.scalars().all()
            return [organization_member_model_to_entity(row) for row in results]
