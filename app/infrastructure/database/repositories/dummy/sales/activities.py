from dataclasses import (
    dataclass,
    field,
)
from uuid import UUID

from domain.sales.entities import ActivityEntity
from domain.sales.interfaces.repositories.activities import BaseActivityRepository


@dataclass
class DummyInMemoryActivityRepository(BaseActivityRepository):
    _saved_activities: list[ActivityEntity] = field(
        default_factory=list,
        kw_only=True,
    )

    async def add(self, activity: ActivityEntity) -> None:
        self._saved_activities.append(activity)

    async def get_by_id(self, activity_id: UUID) -> ActivityEntity | None:
        try:
            return next(activity for activity in self._saved_activities if activity.oid == activity_id)
        except StopIteration:
            return None

    async def get_by_deal_id(self, deal_id: UUID) -> list[ActivityEntity]:
        return [activity for activity in self._saved_activities if activity.deal_id == deal_id]
