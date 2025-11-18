from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.sales.entities import DealEntity
from domain.sales.filters import DealFilters
from domain.sales.services import DealService


@dataclass(frozen=True)
class GetDealByIdQuery(BaseQuery):
    deal_id: UUID


@dataclass(frozen=True)
class GetDealsQuery(BaseQuery):
    filters: DealFilters


@dataclass(frozen=True)
class GetDealByIdQueryHandler(
    BaseQueryHandler[GetDealByIdQuery, DealEntity],
):
    deal_service: DealService

    async def handle(
        self,
        query: GetDealByIdQuery,
    ) -> DealEntity:
        return await self.deal_service.get_deal_by_id(
            deal_id=query.deal_id,
        )


@dataclass(frozen=True)
class GetDealsQueryHandler(
    BaseQueryHandler[
        GetDealsQuery,
        tuple[Iterable[DealEntity], int],
    ],
):
    deal_service: DealService

    async def handle(
        self,
        query: GetDealsQuery,
    ) -> tuple[Iterable[DealEntity], int]:
        deals = await self.deal_service.get_deal_list(query.filters)
        count = await self.deal_service.get_deal_count(query.filters)
        return deals, count
