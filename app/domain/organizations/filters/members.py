from uuid import UUID

from domain.base.filters import BaseFilters
from domain.organizations.value_objects.members import OrganizationMemberRole


class MemberFilters(BaseFilters):
    # Фильтры по организации и пользователю
    organization_id: UUID | None = None
    user_id: UUID | None = None

    # Фильтр по роли
    role: OrganizationMemberRole | None = None
    roles: list[OrganizationMemberRole] | None = None
