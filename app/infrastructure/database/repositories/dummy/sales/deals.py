from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities import DealEntity
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
