from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.base.query import (
    BaseQuery,
    BaseQueryHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.filters import (
    DealFilters,
    DealFunnelFilters,
    DealSummaryFilters,
)
from domain.sales.services import DealService
from domain.sales.value_objects.deals import (
    DealStage,
    DealStatus,
)


@dataclass(frozen=True)
class DealSummaryResult:
    total_count: int
    new_count: int
    in_progress_count: int
    won_count: int
    lost_count: int
    total_won_amount: float
    new_deals_count: int | None = None


@dataclass(frozen=True)
class DealFunnelResult:
    qualification_count: int
    proposal_count: int
    negotiation_count: int
    closed_count: int


@dataclass(frozen=True)
class GetDealSummaryQuery(BaseQuery):
    filters: DealSummaryFilters
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetDealFunnelQuery(BaseQuery):
    filters: DealFunnelFilters
    user_id: UUID
    user_role: str


@dataclass(frozen=True)
class GetDealSummaryQueryHandler(
    BaseQueryHandler[GetDealSummaryQuery, DealSummaryResult],
):
    deal_service: DealService

    def _build_status_filters(
        self,
        organization_id: UUID,
        status: DealStatus,
        user_id: UUID | None,
        created_after: datetime | None = None,
    ) -> DealFilters:
        filters = DealFilters(
            organization_id=organization_id,
            status=[status],
        )
        if user_id:
            filters.owner_id = user_id
        if created_after:
            filters.created_at_from = created_after
        return filters

    async def handle(
        self,
        query: GetDealSummaryQuery,
    ) -> DealSummaryResult:
        role = OrganizationMemberRole(query.user_role)
        user_id = query.user_id if role == OrganizationMemberRole.MEMBER else None

        base_filters = DealFilters(
            organization_id=query.filters.organization_id,
        )
        if user_id:
            base_filters.owner_id = user_id
        if query.filters.created_after:
            base_filters.created_at_from = query.filters.created_after
        if query.filters.status:
            status_enums = []
            for status_str in query.filters.status:
                try:
                    status_enums.append(DealStatus(status_str))
                except ValueError:
                    pass
            if status_enums:
                base_filters.status = status_enums

        total_count = await self.deal_service.get_deal_count(base_filters)

        new_count = await self.deal_service.get_deal_count(
            self._build_status_filters(
                query.filters.organization_id,
                DealStatus.NEW,
                user_id,
                query.filters.created_after,
            ),
        )

        in_progress_count = await self.deal_service.get_deal_count(
            self._build_status_filters(
                query.filters.organization_id,
                DealStatus.IN_PROGRESS,
                user_id,
                query.filters.created_after,
            ),
        )

        won_count = await self.deal_service.get_deal_count(
            self._build_status_filters(
                query.filters.organization_id,
                DealStatus.WON,
                user_id,
                query.filters.created_after,
            ),
        )

        lost_count = await self.deal_service.get_deal_count(
            self._build_status_filters(
                query.filters.organization_id,
                DealStatus.LOST,
                user_id,
                query.filters.created_after,
            ),
        )

        total_won_amount = await self.deal_service.get_total_amount(
            organization_id=query.filters.organization_id,
            status=DealStatus.WON,
            user_id=user_id,
        )

        new_deals_count = None
        if query.filters.created_after:
            new_deals_count = await self.deal_service.get_deal_count(
                self._build_status_filters(
                    query.filters.organization_id,
                    DealStatus.NEW,
                    user_id,
                    query.filters.created_after,
                ),
            )

        return DealSummaryResult(
            total_count=total_count,
            new_count=new_count,
            in_progress_count=in_progress_count,
            won_count=won_count,
            lost_count=lost_count,
            total_won_amount=total_won_amount,
            new_deals_count=new_deals_count,
        )


@dataclass(frozen=True)
class GetDealFunnelQueryHandler(
    BaseQueryHandler[GetDealFunnelQuery, DealFunnelResult],
):
    deal_service: DealService

    def _build_status_enums(self, status_list: list[str] | None) -> list[DealStatus] | None:
        if not status_list:
            return None
        status_enums = []
        for status_str in status_list:
            try:
                status_enums.append(DealStatus(status_str))
            except ValueError:
                pass
        return status_enums if status_enums else None

    def _build_stage_filters(
        self,
        organization_id: UUID,
        stage: DealStage,
        user_id: UUID | None,
        user_role: str,
        status_list: list[str] | None,
    ) -> DealFilters:
        from domain.sales.filters import DealFilters

        filters = DealFilters(
            organization_id=organization_id,
            stage=stage,
        )
        if OrganizationMemberRole(user_role) == OrganizationMemberRole.MEMBER:
            filters.owner_id = user_id
        status_enums = self._build_status_enums(status_list)
        if status_enums:
            filters.status = status_enums
        return filters

    async def handle(
        self,
        query: GetDealFunnelQuery,
    ) -> DealFunnelResult:
        qualification_filters = self._build_stage_filters(
            query.filters.organization_id,
            DealStage.QUALIFICATION,
            query.user_id,
            query.user_role,
            query.filters.status,
        )
        qualification_count = await self.deal_service.get_deal_count(qualification_filters)

        proposal_filters = self._build_stage_filters(
            query.filters.organization_id,
            DealStage.PROPOSAL,
            query.user_id,
            query.user_role,
            query.filters.status,
        )
        proposal_count = await self.deal_service.get_deal_count(proposal_filters)

        negotiation_filters = self._build_stage_filters(
            query.filters.organization_id,
            DealStage.NEGOTIATION,
            query.user_id,
            query.user_role,
            query.filters.status,
        )
        negotiation_count = await self.deal_service.get_deal_count(negotiation_filters)

        closed_filters = self._build_stage_filters(
            query.filters.organization_id,
            DealStage.CLOSED,
            query.user_id,
            query.user_role,
            query.filters.status,
        )
        closed_count = await self.deal_service.get_deal_count(closed_filters)

        return DealFunnelResult(
            qualification_count=qualification_count,
            proposal_count=proposal_count,
            negotiation_count=negotiation_count,
            closed_count=closed_count,
        )
