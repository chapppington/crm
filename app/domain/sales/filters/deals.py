from datetime import datetime
from uuid import UUID

from domain.base.filters import BaseOrganizationSearchFilters
from domain.sales.value_objects.deals import (
    DealStage,
    DealStatus,
)


class DealFilters(BaseOrganizationSearchFilters):
    # Фильтр по связанным сущностям
    contact_id: UUID | None = None
    owner_id: UUID | None = None

    # Фильтры по статусу и стадии
    status: list[DealStatus] | None = None
    stage: DealStage | None = None

    # Фильтр по сумме (диапазон)
    min_amount: float | None = None
    max_amount: float | None = None

    # Фильтр по валюте
    currency: str | None = None

    # Фильтры по датам обновления (диапазон)
    updated_at_from: datetime | None = None
    updated_at_to: datetime | None = None

    # Сортировка
    order_by: str | None = None  # created_at, amount, updated_at
    order: str = "desc"  # asc, desc
