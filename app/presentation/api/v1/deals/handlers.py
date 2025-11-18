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
)
from presentation.api.filters import PaginationOut
from presentation.api.schemas import (
    ApiResponse,
    ErrorResponseSchema,
)
from presentation.api.v1.deals.schemas import (
    CreateDealRequestSchema,
    DealListResponseSchema,
    DealResponseSchema,
    UpdateDealRequestSchema,
)

from application.container import init_container
from application.mediator import Mediator
from application.sales.commands import (
    CreateDealCommand,
    UpdateDealCommand,
)
from application.sales.queries import (
    GetDealByIdQuery,
    GetDealsQuery,
)
from domain.organizations.entities import OrganizationMemberEntity
from domain.sales.filters import DealFilters


router = APIRouter(prefix="/deals", tags=["deals"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[DealListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[DealListResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def get_deals(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status_list: list[str] | None = Query(default=None, alias="status"),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
    stage: str | None = Query(default=None),
    owner_id: UUID | None = Query(default=None),
    order_by: str | None = Query(default=None),
    order: str = Query(default="desc"),
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[DealListResponseSchema]:
    """Получить список сделок с фильтрацией, сортировкой и пагинацией."""
    mediator: Mediator = container.resolve(Mediator)

    filters = DealFilters(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
        min_amount=min_amount,
        max_amount=max_amount,
        order_by=order_by,
        order=order,
    )

    role = member.role.as_generic_type()
    query = GetDealsQuery(
        filters=filters,
        user_id=user_id,
        user_role=role.value,
        owner_id=owner_id,
        status_list=status_list,
        stage=stage,
    )
    deals, total = await mediator.handle_query(query)

    items = [DealResponseSchema.from_entity(deal) for deal in deals]

    pagination = PaginationOut(
        limit=page_size,
        offset=(page - 1) * page_size,
        total=total,
    )

    return ApiResponse[DealListResponseSchema](
        data=DealListResponseSchema(
            items=items,
            pagination=pagination,
        ),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[DealResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[DealResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def create_deal(
    request: CreateDealRequestSchema,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[DealResponseSchema]:
    """Создать новую сделку."""
    mediator: Mediator = container.resolve(Mediator)

    command = CreateDealCommand(
        organization_id=organization_id,
        contact_id=request.contact_id,
        owner_user_id=user_id,
        title=request.title,
        amount=request.amount,
        currency=request.currency,
    )

    deal, *_ = await mediator.handle_command(command)

    return ApiResponse[DealResponseSchema](
        data=DealResponseSchema.from_entity(deal),
    )


@router.get(
    "/{deal_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[DealResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[DealResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
    },
)
async def get_deal(
    deal_id: UUID,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[DealResponseSchema]:
    """Получить сделку по ID."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    query = GetDealByIdQuery(
        deal_id=deal_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
    )
    deal = await mediator.handle_query(query)

    return ApiResponse[DealResponseSchema](
        data=DealResponseSchema.from_entity(deal),
    )


@router.patch(
    "/{deal_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[DealResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[DealResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def update_deal(
    deal_id: UUID,
    request: UpdateDealRequestSchema,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[DealResponseSchema]:
    """Обновить сделку (статус и/или стадию)."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    command = UpdateDealCommand(
        deal_id=deal_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
        new_status=request.status,
        new_stage=request.stage,
    )
    deal, *_ = await mediator.handle_command(command)

    return ApiResponse[DealResponseSchema](
        data=DealResponseSchema.from_entity(deal),
    )
