from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from uuid import UUID

from domain.sales.entities import DealEntity
from domain.sales.filters import DealFilters
from domain.sales.value_objects.deals import DealStatus


class BaseDealRepository(ABC):
    @abstractmethod
    async def add(self, deal: DealEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, deal_id: UUID) -> DealEntity | None: ...

    @abstractmethod
    async def update(self, deal: DealEntity) -> None: ...

    @abstractmethod
    async def get_by_contact_id(self, contact_id: UUID) -> list[DealEntity]: ...

    @abstractmethod
    async def get_list(
        self,
        filters: DealFilters,
    ) -> Iterable[DealEntity]: ...

    @abstractmethod
    async def get_count(
        self,
        filters: DealFilters,
    ) -> int: ...

    @abstractmethod
    async def get_total_amount(
        self,
        organization_id: UUID,
        status: DealStatus,
        user_id: UUID | None = None,
    ) -> float: ...
