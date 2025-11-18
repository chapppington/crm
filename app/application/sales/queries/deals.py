from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import DealEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    InvalidDealStageException,
    InvalidDealStatusException,
    ResourceNotFoundInOrganizationException,
)
from domain.sales.filters import DealFilters
from domain.sales.services import DealService
from domain.sales.value_objects.deals import (
    DealStage,
    DealStatus,
)


@dataclass(frozen=True)
class GetDealByIdQuery(BaseQuery):
    deal_id: UUID
    organization_id: UUID
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetDealsQuery(BaseQuery):
    filters: DealFilters
    user_id: UUID
    user_role: str
    owner_id: UUID | None = None
    status_list: list[str] | None = None
    stage: str | None = None


@dataclass(frozen=True)
class GetDealByIdQueryHandler(
    BaseQueryHandler[GetDealByIdQuery, DealEntity],
):
    deal_service: DealService

    async def handle(
        self,
        query: GetDealByIdQuery,
    ) -> DealEntity:
        deal = await self.deal_service.get_deal_by_id(
            deal_id=query.deal_id,
        )

        # Проверка принадлежности к организации
        if deal.organization_id != query.organization_id:
            raise ResourceNotFoundInOrganizationException(
                resource_type="Deal",
                resource_id=query.deal_id,
                organization_id=query.organization_id,
            )

        # Проверка прав доступа
        role = OrganizationMemberRole(query.user_role)
        if role == OrganizationMemberRole.MEMBER and deal.owner_user_id != query.user_id:
            raise AccessDeniedException(
                resource_type="Deal",
                resource_id=query.deal_id,
                user_id=query.user_id,
            )

        return deal


@dataclass(frozen=True)
class GetDealsQueryHandler(
    BaseQueryHandler[
        GetDealsQuery,
        tuple[Iterable[DealEntity], int],
    ],
):
    deal_service: DealService

    async def handle(
        self,
        query: GetDealsQuery,
    ) -> tuple[Iterable[DealEntity], int]:
        role = OrganizationMemberRole(query.user_role)

        # Проверка прав на фильтрацию по owner_id
        if query.owner_id is not None and role == OrganizationMemberRole.MEMBER:
            raise AccessDeniedException(
                resource_type="Deal",
                resource_id=query.user_id,
                user_id=query.user_id,
            )

        # Преобразуем статусы из строк в enum
        status_enums = None
        if query.status_list:
            try:
                status_enums = [DealStatus(s) for s in query.status_list]
            except ValueError:
                invalid_statuses = [s for s in query.status_list if s not in [st.value for st in DealStatus]]
                raise InvalidDealStatusException(status=invalid_statuses[0] if invalid_statuses else "")

        # Преобразуем stage из строки в enum
        stage_enum = None
        if query.stage:
            try:
                stage_enum = DealStage(query.stage)
            except ValueError:
                raise InvalidDealStageException(stage=query.stage)

        # Обновляем filters с преобразованными значениями
        filters_dict = query.filters.model_dump()
        if status_enums is not None:
            filters_dict["status"] = status_enums
        if stage_enum is not None:
            filters_dict["stage"] = stage_enum
        if query.owner_id is not None:
            filters_dict["owner_id"] = query.owner_id

        filters = DealFilters.model_validate(filters_dict)

        # Для member автоматически фильтруем по его сделкам, если owner_id не указан
        if role == OrganizationMemberRole.MEMBER and filters.owner_id is None:
            filters = DealFilters.model_validate(
                {**filters.model_dump(), "owner_id": query.user_id},
            )

        deals = await self.deal_service.get_deal_list(filters)
        count = await self.deal_service.get_deal_count(filters)
        return deals, count
