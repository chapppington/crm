from domain.base.filters import BaseSearchFilters


class OrganizationFilters(BaseSearchFilters):
    # Текстовый поиск по name
    name: str | None = None
