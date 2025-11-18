from abc import (
    ABC,
    abstractmethod,
)
from uuid import UUID

from domain.organizations.entities import OrganizationEntity


class BaseOrganizationRepository(ABC):
    """Интерфейс репозитория для организаций."""

    @abstractmethod
    async def add(self, organization: OrganizationEntity) -> None:
        """Добавить организацию."""

    @abstractmethod
    async def get_by_id(self, organization_id: UUID) -> OrganizationEntity | None:
        """Получить организацию по ID."""
