from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)

from presentation.api.dependencies import (
    get_current_user_id,
    get_organization_id,
    get_organization_member,
    init_container,
)
from presentation.api.schemas import (
    ApiResponse,
    ErrorResponseSchema,
)
from presentation.api.v1.analytics.schemas import (
    DealFunnelResponseSchema,
    DealSummaryResponseSchema,
)

from application.mediator import Mediator
from application.sales.queries.analytics import (
    GetDealFunnelQuery,
    GetDealSummaryQuery,
)
from domain.organizations.entities import OrganizationMemberEntity
from domain.sales.filters import (
    DealFunnelFilters,
    DealSummaryFilters,
)


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/deals/summary",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[DealSummaryResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[DealSummaryResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def get_deal_summary(
    created_after: datetime | None = Query(default=None, description="Filter deals created after this date"),
    status_list: list[str] | None = Query(default=None, description="Filter by deal statuses"),
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[DealSummaryResponseSchema]:
    """Получить сводку по сделкам."""
    mediator: Mediator = container.resolve(Mediator)

    filters = DealSummaryFilters(
        organization_id=organization_id,
        created_after=created_after,
        status=status_list,
    )

    role = member.role.as_generic_type()
    query = GetDealSummaryQuery(
        filters=filters,
        user_id=user_id,
        user_role=role.value,
    )
    result = await mediator.handle_query(query)

    return ApiResponse[DealSummaryResponseSchema](
        data=DealSummaryResponseSchema.from_result(result),
    )


@router.get(
    "/deals/funnel",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[DealFunnelResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[DealFunnelResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def get_deal_funnel(
    status_list: list[str] | None = Query(default=None, description="Filter by deal statuses"),
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[DealFunnelResponseSchema]:
    """Получить воронку продаж по стадиям."""
    mediator: Mediator = container.resolve(Mediator)

    filters = DealFunnelFilters(
        organization_id=organization_id,
        status=status_list,
    )

    role = member.role.as_generic_type()
    query = GetDealFunnelQuery(
        filters=filters,
        user_id=user_id,
        user_role=role.value,
    )
    result = await mediator.handle_query(query)

    return ApiResponse[DealFunnelResponseSchema](
        data=DealFunnelResponseSchema.from_result(result),
    )
