from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.sales.activity import (
    activity_entity_to_model,
    activity_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.sales.activity import ActivityModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.sales.entities.activities import ActivityEntity
from domain.sales.interfaces.repositories.activities import BaseActivityRepository


@dataclass
class SQLAlchemyActivityRepository(BaseActivityRepository):
    database: Database

    async def add(self, activity: ActivityEntity) -> None:
        async with self.database.get_session() as session:
            activity_model = activity_entity_to_model(activity)
            session.add(activity_model)
            await session.commit()

    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(ActivityModel)
                .where(ActivityModel.oid == activity_id)
                .options(
                    selectinload(ActivityModel.deal),
                    selectinload(ActivityModel.author),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return activity_model_to_entity(result) if result else None

    async def get_by_deal_id(self, deal_id: UUID) -> list[ActivityEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(ActivityModel)
                .where(ActivityModel.deal_id == deal_id)
                .options(
                    selectinload(ActivityModel.deal),
                    selectinload(ActivityModel.author),
                )
                .order_by(ActivityModel.created_at.desc())
            )
            res = await session.execute(stmt)
            results = res.scalars().all()
            return [activity_model_to_entity(row) for row in results]
