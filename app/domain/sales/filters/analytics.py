from datetime import datetime

from domain.base.filters import BaseOrganizationFilters


class DealSummaryFilters(BaseOrganizationFilters):
    # Фильтр по дате создания (для подсчета новых сделок за последние N дней)
    created_after: datetime | None = None

    # Фильтр по статусам (если нужно ограничить сводку определенными статусами)
    status: list[str] | None = None


class DealFunnelFilters(BaseOrganizationFilters):
    # Фильтр по статусам (если нужно ограничить воронку определенными статусами)
    status: list[str] | None = None
