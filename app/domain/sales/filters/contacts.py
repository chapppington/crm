from uuid import UUID

from domain.base.filters import BaseOrganizationSearchFilters


class ContactFilters(BaseOrganizationSearchFilters):
    # Фильтр по владельцу
    owner_id: UUID | None = None

    # Текстовые поля (поиск по частичному совпадению)
    name: str | None = None
    email: str | None = None
    phone: str | None = None
