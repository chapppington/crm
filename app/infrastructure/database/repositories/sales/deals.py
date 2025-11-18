from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.sales.deal import (
    deal_entity_to_model,
    deal_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.sales.deal import DealModel
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from domain.sales.entities.deals import DealEntity
from domain.sales.filters.deals import DealFilters
from domain.sales.interfaces.repositories.deals import BaseDealRepository
from domain.sales.value_objects.deals import DealStatus


@dataclass
class SQLAlchemyDealRepository(BaseDealRepository):
    database: Database

    def _build_query(self, stmt: Select, filters: DealFilters) -> Select:
        if filters.organization_id:
            stmt = stmt.where(DealModel.organization_id == filters.organization_id)
        if filters.contact_id:
            stmt = stmt.where(DealModel.contact_id == filters.contact_id)
        if filters.owner_id:
            stmt = stmt.where(DealModel.owner_id == filters.owner_id)
        if filters.id:
            stmt = stmt.where(DealModel.oid == filters.id)
        if filters.ids:
            stmt = stmt.where(DealModel.oid.in_(filters.ids))
        if filters.status:
            status_values = [s.value for s in filters.status]
            stmt = stmt.where(DealModel.status.in_(status_values))
        if filters.stage:
            stmt = stmt.where(DealModel.stage == filters.stage.value)
        if filters.min_amount is not None:
            stmt = stmt.where(DealModel.amount >= filters.min_amount)
        if filters.max_amount is not None:
            stmt = stmt.where(DealModel.amount <= filters.max_amount)
        if filters.currency:
            stmt = stmt.where(DealModel.currency == filters.currency)
        if filters.updated_at_from:
            stmt = stmt.where(DealModel.updated_at >= filters.updated_at_from)
        if filters.updated_at_to:
            stmt = stmt.where(DealModel.updated_at <= filters.updated_at_to)
        if filters.search:
            stmt = stmt.where(DealModel.title.ilike(f"%{filters.search}%"))
        if filters.created_at_from:
            stmt = stmt.where(DealModel.created_at >= filters.created_at_from)
        if filters.created_at_to:
            stmt = stmt.where(DealModel.created_at <= filters.created_at_to)
        return stmt

    async def add(self, deal: DealEntity) -> None:
        async with self.database.get_session() as session:
            deal_model = deal_entity_to_model(deal)
            session.add(deal_model)
            await session.commit()

    async def get_by_id(self, deal_id: UUID) -> DealEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(DealModel)
                .where(DealModel.oid == deal_id)
                .options(
                    selectinload(DealModel.organization),
                    selectinload(DealModel.contact),
                    selectinload(DealModel.owner),
                    selectinload(DealModel.tasks),
                    selectinload(DealModel.activities),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return deal_model_to_entity(result) if result else None

    async def update(self, deal: DealEntity) -> None:
        async with self.database.get_session() as session:
            stmt = select(DealModel).where(DealModel.oid == deal.oid)
            res = await session.execute(stmt)
            deal_model = res.scalar_one_or_none()
            if deal_model:
                updated_model = deal_entity_to_model(deal)
                deal_model.title = updated_model.title
                deal_model.amount = updated_model.amount
                deal_model.currency = updated_model.currency
                deal_model.status = updated_model.status
                deal_model.stage = updated_model.stage
                deal_model.updated_at = updated_model.updated_at
                await session.commit()

    async def get_by_contact_id(self, contact_id: UUID) -> list[DealEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(DealModel)
                .where(DealModel.contact_id == contact_id)
                .options(
                    selectinload(DealModel.organization),
                    selectinload(DealModel.contact),
                    selectinload(DealModel.owner),
                    selectinload(DealModel.tasks),
                    selectinload(DealModel.activities),
                )
            )
            res = await session.execute(stmt)
            results = res.scalars().all()
            return [deal_model_to_entity(row) for row in results]

    async def get_list(
        self,
        filters: DealFilters,
    ) -> Iterable[DealEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = select(DealModel).options(
                selectinload(DealModel.organization),
                selectinload(DealModel.contact),
                selectinload(DealModel.owner),
                selectinload(DealModel.tasks),
                selectinload(DealModel.activities),
            )
            stmt = self._build_query(stmt, filters)

            if filters.order_by:
                order_column = getattr(DealModel, filters.order_by, None)
                if order_column:
                    if filters.order == "desc":
                        stmt = stmt.order_by(order_column.desc())
                    else:
                        stmt = stmt.order_by(order_column.asc())
            else:
                stmt = stmt.order_by(DealModel.created_at.desc())

            offset = (filters.page - 1) * filters.page_size
            stmt = stmt.offset(offset).limit(filters.page_size)

            res = await session.execute(stmt)
            results = res.scalars().all()
            return [deal_model_to_entity(row) for row in results]

    async def get_count(
        self,
        filters: DealFilters,
    ) -> int:
        async with self.database.get_read_only_session() as session:
            stmt = select(func.count(DealModel.oid))
            stmt = self._build_query(stmt, filters)

            res = await session.execute(stmt)
            return res.scalar_one() or 0

    async def get_total_amount(
        self,
        organization_id: UUID,
        status: DealStatus,
        user_id: UUID | None = None,
    ) -> float:
        async with self.database.get_read_only_session() as session:
            stmt = select(func.coalesce(func.sum(DealModel.amount), 0))
            stmt = stmt.where(DealModel.organization_id == organization_id)
            stmt = stmt.where(DealModel.status == status.value)
            if user_id:
                stmt = stmt.where(DealModel.owner_id == user_id)

            res = await session.execute(stmt)
            result = res.scalar_one()
            return float(result) if result else 0.0
