from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities.deals import DealEntity
from domain.sales.filters.deals import DealFilters
from domain.sales.interfaces.repositories.deals import BaseDealRepository
from domain.sales.value_objects.deals import DealStatus


@dataclass
class DummyInMemoryDealRepository(BaseDealRepository):
    _saved_deals: list[DealEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    def _filter_items(self, items: list[DealEntity], filters: DealFilters) -> list[DealEntity]:
        result = list(items)

        if filters.organization_id:
            result = [d for d in result if d.organization_id == filters.organization_id]
        if filters.contact_id:
            result = [d for d in result if d.contact_id == filters.contact_id]
        if filters.owner_id:
            result = [d for d in result if d.owner_user_id == filters.owner_id]
        if filters.id:
            result = [d for d in result if d.oid == filters.id]
        if filters.ids:
            result = [d for d in result if d.oid in filters.ids]
        if filters.status:
            status_values = [s.value for s in filters.status]
            result = [d for d in result if d.status.as_generic_type().value in status_values]
        if filters.stage:
            result = [d for d in result if d.stage.as_generic_type() == filters.stage]
        if filters.min_amount is not None:
            result = [d for d in result if d.amount.as_generic_type() >= filters.min_amount]
        if filters.max_amount is not None:
            result = [d for d in result if d.amount.as_generic_type() <= filters.max_amount]
        if filters.currency:
            result = [d for d in result if d.currency.as_generic_type() == filters.currency]
        if filters.updated_at_from:
            result = [d for d in result if d.updated_at >= filters.updated_at_from]
        if filters.updated_at_to:
            result = [d for d in result if d.updated_at <= filters.updated_at_to]
        if filters.search:
            search_lower = filters.search.lower()
            result = [d for d in result if search_lower in d.title.as_generic_type().lower()]
        if filters.created_at_from:
            result = [d for d in result if d.created_at >= filters.created_at_from]
        if filters.created_at_to:
            result = [d for d in result if d.created_at <= filters.created_at_to]

        return result

    async def add(self, deal: DealEntity) -> None:
        self._saved_deals.append(deal)

    async def get_by_id(self, deal_id: UUID) -> DealEntity | None:
        try:
            return next(deal for deal in self._saved_deals if deal.oid == deal_id)
        except StopIteration:
            return None

    async def update(self, deal: DealEntity) -> None:
        for i, saved_deal in enumerate(self._saved_deals):
            if saved_deal.oid == deal.oid:
                self._saved_deals[i] = deal
                return

    async def get_by_contact_id(self, contact_id: UUID) -> list[DealEntity]:
        return [deal for deal in self._saved_deals if deal.contact_id == contact_id]

    async def get_list(
        self,
        filters: DealFilters,
    ) -> Iterable[DealEntity]:
        result = self._filter_items(self._saved_deals, filters)

        offset = (filters.page - 1) * filters.page_size
        limit = filters.page_size

        return result[offset : offset + limit]

    async def get_count(
        self,
        filters: DealFilters,
    ) -> int:
        result = self._filter_items(self._saved_deals, filters)
        return len(result)

    async def get_total_amount(
        self,
        organization_id: UUID,
        status: DealStatus,
        user_id: UUID | None = None,
    ) -> float:
        filters = DealFilters(
            organization_id=organization_id,
            status=[status],
        )
        if user_id:
            filters.owner_id = user_id
        result = self._filter_items(self._saved_deals, filters)
        return sum(deal.amount.as_generic_type() for deal in result)
