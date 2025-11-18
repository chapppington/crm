from abc import (
    ABC,
    abstractmethod,
)
from collections.abc import Iterable
from uuid import UUID

from domain.sales.entities import ContactEntity
from domain.sales.filters import ContactFilters


class BaseContactRepository(ABC):
    @abstractmethod
    async def add(self, contact: ContactEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, contact_id: UUID) -> ContactEntity | None: ...

    @abstractmethod
    async def delete(self, contact_id: UUID) -> None: ...

    @abstractmethod
    async def get_list(
        self,
        filters: ContactFilters,
    ) -> Iterable[ContactEntity]: ...

    @abstractmethod
    async def get_count(
        self,
        filters: ContactFilters,
    ) -> int: ...
