from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.sales.contact import (
    contact_entity_to_model,
    contact_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.sales.contact import ContactModel
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from domain.sales.entities.contacts import ContactEntity
from domain.sales.filters.contacts import ContactFilters
from domain.sales.interfaces.repositories.contacts import BaseContactRepository


@dataclass
class SQLAlchemyContactRepository(BaseContactRepository):
    database: Database

    def _build_query(self, stmt: Select, filters: ContactFilters) -> Select:
        if filters.organization_id:
            stmt = stmt.where(ContactModel.organization_id == filters.organization_id)
        if filters.owner_id:
            stmt = stmt.where(ContactModel.owner_id == filters.owner_id)
        if filters.id:
            stmt = stmt.where(ContactModel.oid == filters.id)
        if filters.ids:
            stmt = stmt.where(ContactModel.oid.in_(filters.ids))
        if filters.name:
            stmt = stmt.where(ContactModel.name.ilike(f"%{filters.name}%"))
        if filters.email:
            stmt = stmt.where(ContactModel.email.ilike(f"%{filters.email}%"))
        if filters.phone:
            stmt = stmt.where(ContactModel.phone.ilike(f"%{filters.phone}%"))
        if filters.search:
            stmt = stmt.where(
                (ContactModel.name.ilike(f"%{filters.search}%"))
                | (ContactModel.email.ilike(f"%{filters.search}%"))
                | (ContactModel.phone.ilike(f"%{filters.search}%")),
            )
        if filters.created_at_from:
            stmt = stmt.where(ContactModel.created_at >= filters.created_at_from)
        if filters.created_at_to:
            stmt = stmt.where(ContactModel.created_at <= filters.created_at_to)
        return stmt

    async def add(self, contact: ContactEntity) -> None:
        async with self.database.get_session() as session:
            contact_model = contact_entity_to_model(contact)
            session.add(contact_model)
            await session.commit()

    async def get_by_id(self, contact_id: UUID) -> ContactEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(ContactModel)
                .where(ContactModel.oid == contact_id)
                .options(
                    selectinload(ContactModel.organization),
                    selectinload(ContactModel.owner),
                    selectinload(ContactModel.deals),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return contact_model_to_entity(result) if result else None

    async def delete(self, contact_id: UUID) -> None:
        async with self.database.get_session() as session:
            stmt = select(ContactModel).where(ContactModel.oid == contact_id)
            res = await session.execute(stmt)
            contact = res.scalar_one_or_none()
            if contact:
                await session.delete(contact)
                await session.commit()

    async def get_list(
        self,
        filters: ContactFilters,
    ) -> Iterable[ContactEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = select(ContactModel).options(
                selectinload(ContactModel.organization),
                selectinload(ContactModel.owner),
                selectinload(ContactModel.deals),
            )
            stmt = self._build_query(stmt, filters)

            offset = (filters.page - 1) * filters.page_size
            stmt = stmt.offset(offset).limit(filters.page_size)

            res = await session.execute(stmt)
            results = res.scalars().all()
            return [contact_model_to_entity(row) for row in results]

    async def get_count(
        self,
        filters: ContactFilters,
    ) -> int:
        async with self.database.get_read_only_session() as session:
            stmt = select(func.count(ContactModel.oid))
            stmt = self._build_query(stmt, filters)

            res = await session.execute(stmt)
            return res.scalar_one() or 0
