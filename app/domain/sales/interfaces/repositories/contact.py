from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.sales.entities import ContactEntity


class BaseContactRepository(ABC):
    @abstractmethod
    async def add(self, contact: ContactEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, contact_id: UUID) -> ContactEntity | None: ...

    @abstractmethod
    async def delete(self, contact_id: UUID) -> None: ...
