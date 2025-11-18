from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from infrastructure.database.converters.sales.task import (
    task_entity_to_model,
    task_model_to_entity,
)
from infrastructure.database.gateways.postgres import Database
from infrastructure.database.models.sales.deal import DealModel
from infrastructure.database.models.sales.task import TaskModel
from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from domain.sales.entities.tasks import TaskEntity
from domain.sales.filters.tasks import TaskFilters
from domain.sales.interfaces.repositories.tasks import BaseTaskRepository


@dataclass
class SQLAlchemyTaskRepository(BaseTaskRepository):
    database: Database

    def _build_query(self, stmt: Select, filters: TaskFilters) -> Select:
        if filters.deal_id:
            stmt = stmt.where(TaskModel.deal_id == filters.deal_id)
        if filters.id:
            stmt = stmt.where(TaskModel.oid == filters.id)
        if filters.ids:
            stmt = stmt.where(TaskModel.oid.in_(filters.ids))
        if filters.only_open is not None:
            if filters.only_open:
                stmt = stmt.where(TaskModel.is_done.is_(False))
        if filters.is_done is not None:
            stmt = stmt.where(TaskModel.is_done == filters.is_done)
        if filters.due_before:
            stmt = stmt.where(TaskModel.due_date <= filters.due_before)
        if filters.due_after:
            stmt = stmt.where(TaskModel.due_date >= filters.due_after)
        if filters.organization_id:
            stmt = stmt.join(DealModel).where(DealModel.organization_id == filters.organization_id)
        if filters.search:
            stmt = stmt.where(
                (TaskModel.title.ilike(f"%{filters.search}%")) | (TaskModel.description.ilike(f"%{filters.search}%")),
            )
        if filters.created_at_from:
            stmt = stmt.where(TaskModel.created_at >= filters.created_at_from)
        if filters.created_at_to:
            stmt = stmt.where(TaskModel.created_at <= filters.created_at_to)
        return stmt

    async def add(self, task: TaskEntity) -> None:
        async with self.database.get_session() as session:
            task_model = task_entity_to_model(task)
            session.add(task_model)
            await session.commit()

    async def get_by_id(self, task_id: UUID) -> TaskEntity | None:
        async with self.database.get_read_only_session() as session:
            stmt = (
                select(TaskModel)
                .where(TaskModel.oid == task_id)
                .options(
                    selectinload(TaskModel.deal),
                )
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            return task_model_to_entity(result) if result else None

    async def update(self, task: TaskEntity) -> None:
        async with self.database.get_session() as session:
            stmt = select(TaskModel).where(TaskModel.oid == task.oid)
            res = await session.execute(stmt)
            task_model = res.scalar_one_or_none()
            if task_model:
                updated_model = task_entity_to_model(task)
                task_model.title = updated_model.title
                task_model.description = updated_model.description
                task_model.due_date = updated_model.due_date
                task_model.is_done = updated_model.is_done
                task_model.updated_at = updated_model.updated_at
                await session.commit()

    async def get_list(
        self,
        filters: TaskFilters,
    ) -> Iterable[TaskEntity]:
        async with self.database.get_read_only_session() as session:
            stmt = select(TaskModel).options(
                selectinload(TaskModel.deal),
            )
            stmt = self._build_query(stmt, filters)

            offset = (filters.page - 1) * filters.page_size
            stmt = stmt.offset(offset).limit(filters.page_size)

            res = await session.execute(stmt)
            results = res.scalars().all()
            return [task_model_to_entity(row) for row in results]

    async def get_count(
        self,
        filters: TaskFilters,
    ) -> int:
        async with self.database.get_read_only_session() as session:
            stmt = select(func.count(TaskModel.oid))
            stmt = self._build_query(stmt, filters)

            res = await session.execute(stmt)
            return res.scalar_one() or 0
