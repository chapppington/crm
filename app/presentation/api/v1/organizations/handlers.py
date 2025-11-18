from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    status,
)

from presentation.api.dependencies import get_current_user_id
from presentation.api.schemas import (
    ApiResponse,
    ErrorResponseSchema,
)
from presentation.api.v1.organizations.schemas import (
    CreateOrganizationRequestSchema,
    GetUserOrganizationsResponseSchema,
    OrganizationMemberResponseSchema,
    OrganizationResponseSchema,
)

from application.container import init_container
from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    CreateOrganizationCommand,
)
from application.organizations.queries import GetUserOrganizationsQuery


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[OrganizationResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[OrganizationResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponseSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponseSchema},
    },
)
async def create_organization(
    request: CreateOrganizationRequestSchema,
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[OrganizationResponseSchema]:
    """Создать новую организацию и добавить текущего пользователя как owner."""
    mediator: Mediator = container.resolve(Mediator)

    # Создаем организацию
    create_org_command = CreateOrganizationCommand(name=request.name)
    org_results = await mediator.handle_command(create_org_command)
    organization = org_results[0]

    # Добавляем создателя как owner
    add_member_command = AddMemberCommand(
        organization_id=organization.oid,
        user_id=user_id,
        role="owner",
    )
    await mediator.handle_command(add_member_command)

    return ApiResponse[OrganizationResponseSchema](
        data=OrganizationResponseSchema.from_entity(organization),
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[GetUserOrganizationsResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[GetUserOrganizationsResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
    },
)
async def get_user_organizations(
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[GetUserOrganizationsResponseSchema]:
    """Получить список организаций текущего пользователя."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetUserOrganizationsQuery(user_id=user_id)
    members, organizations_map = await mediator.handle_query(query)

    # Используем загруженные организации из одного запроса
    organizations_data = []
    for member in members:
        organization = organizations_map.get(member.organization_id)
        organizations_data.append(
            OrganizationMemberResponseSchema.from_entity(
                member=member,
                organization=organization,
            ),
        )

    return ApiResponse[GetUserOrganizationsResponseSchema](
        data=GetUserOrganizationsResponseSchema(organizations=organizations_data),
    )
