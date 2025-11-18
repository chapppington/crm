from domain.base.filters import BaseSearchFilters


class UserFilters(BaseSearchFilters):
    # Текстовые поля (поиск по частичному совпадению)
    email: str | None = None
    name: str | None = None
