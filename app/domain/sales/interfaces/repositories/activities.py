from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.sales.entities import ActivityEntity


class BaseActivityRepository(ABC):
    @abstractmethod
    async def add(self, activity: ActivityEntity) -> None: ...

    @abstractmethod
    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None: ...

    @abstractmethod
    async def get_by_deal_id(self, deal_id: UUID) -> list[ActivityEntity]: ...
