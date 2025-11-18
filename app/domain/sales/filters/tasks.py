from datetime import date
from uuid import UUID

from domain.base.filters import BaseOrganizationSearchFilters


class TaskFilters(BaseOrganizationSearchFilters):
    # Фильтр по сделке
    deal_id: UUID | None = None

    # Фильтр по статусу выполнения
    only_open: bool | None = None  # только is_done=false

    # Фильтр по сроку выполнения (диапазон)
    due_before: date | None = None
    due_after: date | None = None

    # Фильтр по статусу выполнения
    is_done: bool | None = None
