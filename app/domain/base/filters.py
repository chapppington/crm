from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseFilters(BaseModel):
    # ID фильтры
    id: UUID | None = None
    ids: list[UUID] | None = None

    # Фильтры по датам создания (диапазон)
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None

    # Пагинация
    page: int = 1
    page_size: int = 20


class BaseOrganizationFilters(BaseFilters):
    # Multi-tenant фильтр (обязателен для всех запросов)
    organization_id: UUID | None = None


class BaseSearchFilters(BaseFilters):
    # Общий поиск по текстовым полям
    search: str | None = None


class BaseOrganizationSearchFilters(BaseOrganizationFilters, BaseSearchFilters):
    pass
