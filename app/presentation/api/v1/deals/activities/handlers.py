from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from presentation.api.dependencies import (
    get_current_user_id,
    get_organization_id,
    get_organization_member,
)
from presentation.api.schemas import ApiResponse
from presentation.api.v1.deals.activities.schemas import (
    ActivityListResponseSchema,
    ActivityResponseSchema,
    CreateCommentRequestSchema,
)

from application.container import init_container
from application.mediator import Mediator
from application.sales.commands import CreateCommentActivityCommand
from application.sales.queries import GetActivitiesByDealIdQuery
from domain.organizations.entities import OrganizationMemberEntity


router = APIRouter(prefix="/{deal_id}/activities", tags=["activities"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ActivityListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[ActivityListResponseSchema]},
    },
)
async def get_deal_activities(
    deal_id: UUID,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[ActivityListResponseSchema]:
    """Получить список активностей по сделке."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    query = GetActivitiesByDealIdQuery(
        deal_id=deal_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
    )
    activities = await mediator.handle_query(query)

    items = [ActivityResponseSchema.from_entity(activity) for activity in activities]

    return ApiResponse[ActivityListResponseSchema](
        data=ActivityListResponseSchema(items=items),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ActivityResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[ActivityResponseSchema]},
    },
)
async def create_deal_comment(
    deal_id: UUID,
    request: CreateCommentRequestSchema,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[ActivityResponseSchema]:
    """Создать комментарий к сделке."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    command = CreateCommentActivityCommand(
        deal_id=deal_id,
        text=request.text,
        author_user_id=user_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
    )

    activity, *_ = await mediator.handle_command(command)

    return ApiResponse[ActivityResponseSchema](
        data=ActivityResponseSchema.from_entity(activity),
    )
