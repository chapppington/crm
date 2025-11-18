from collections.abc import Iterable
from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities import DealEntity
from domain.sales.filters import DealFilters
from domain.sales.interfaces.repositories.deals import BaseDealRepository


@dataclass
class DummyInMemoryDealRepository(BaseDealRepository):
    _saved_deals: list[DealEntity] = field(
        default_factory=list,
        kw_only=True,
    )

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
        result = list(self._saved_deals)

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
            result = [d for d in result if d.status.as_generic_type() in filters.status]
        if filters.stage:
            result = [d for d in result if d.stage.as_generic_type() == filters.stage]
        if filters.min_amount is not None:
            result = [d for d in result if d.amount.as_generic_type() >= filters.min_amount]
        if filters.max_amount is not None:
            result = [d for d in result if d.amount.as_generic_type() <= filters.max_amount]

        offset = (filters.page - 1) * filters.page_size
        limit = filters.page_size

        return result[offset : offset + limit]

    async def get_count(
        self,
        filters: DealFilters,
    ) -> int:
        result = list(self._saved_deals)

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
            result = [d for d in result if d.status.as_generic_type() in filters.status]
        if filters.stage:
            result = [d for d in result if d.stage.as_generic_type() == filters.stage]
        if filters.min_amount is not None:
            result = [d for d in result if d.amount.as_generic_type() >= filters.min_amount]
        if filters.max_amount is not None:
            result = [d for d in result if d.amount.as_generic_type() <= filters.max_amount]

        return len(result)
