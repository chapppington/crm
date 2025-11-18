from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.organizations.entities import OrganizationMemberEntity


class BaseOrganizationMemberRepository(ABC):
    """Интерфейс репозитория для участников организаций."""

    @abstractmethod
    async def add(self, member: OrganizationMemberEntity) -> None:
        """Добавить участника."""

    @abstractmethod
    async def get_by_id(self, member_id: UUID) -> OrganizationMemberEntity | None:
        """Получить участника по ID."""

    @abstractmethod
    async def get_by_organization_and_user(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMemberEntity | None:
        """Получить участника по организации и пользователю."""

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationMemberEntity]:
        """Получить все организации пользователя."""
