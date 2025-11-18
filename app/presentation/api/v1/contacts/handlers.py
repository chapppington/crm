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
from presentation.api.schemas import ApiResponse
from presentation.api.v1.contacts.schemas import (
    ContactListResponseSchema,
    ContactResponseSchema,
    CreateContactRequestSchema,
)

from application.container import init_container
from application.mediator import Mediator
from application.sales.commands import (
    CreateContactCommand,
    DeleteContactCommand,
)
from application.sales.queries import (
    GetContactByIdQuery,
    GetContactsQuery,
)
from domain.organizations.entities import OrganizationMemberEntity
from domain.sales.filters import ContactFilters


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ContactListResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[ContactListResponseSchema]},
    },
)
async def get_contacts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    owner_id: UUID | None = Query(default=None),
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[ContactListResponseSchema]:
    """Получить список контактов с фильтрацией и пагинацией."""
    mediator: Mediator = container.resolve(Mediator)

    filters = ContactFilters(
        organization_id=organization_id,
        page=page,
        page_size=page_size,
        search=search,
        owner_id=owner_id,
    )

    role = member.role.as_generic_type()
    query = GetContactsQuery(
        filters=filters,
        user_id=user_id,
        user_role=role.value,
        owner_id=owner_id,
    )
    contacts, total = await mediator.handle_query(query)

    items = [ContactResponseSchema.from_entity(contact) for contact in contacts]

    pagination = PaginationOut(
        limit=page_size,
        offset=(page - 1) * page_size,
        total=total,
    )

    return ApiResponse[ContactListResponseSchema](
        data=ContactListResponseSchema(
            items=items,
            pagination=pagination,
        ),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ContactResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[ContactResponseSchema]},
    },
)
async def create_contact(
    request: CreateContactRequestSchema,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> ApiResponse[ContactResponseSchema]:
    """Создать новый контакт."""
    mediator: Mediator = container.resolve(Mediator)

    command = CreateContactCommand(
        organization_id=organization_id,
        owner_user_id=user_id,
        name=request.name,
        email=request.email,
        phone=request.phone,
    )

    results = await mediator.handle_command(command)
    contact = results[0]

    return ApiResponse[ContactResponseSchema](
        data=ContactResponseSchema.from_entity(contact),
    )


@router.get(
    "/{contact_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[ContactResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[ContactResponseSchema]},
    },
)
async def get_contact(
    contact_id: UUID,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> ApiResponse[ContactResponseSchema]:
    """Получить контакт по ID."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    query = GetContactByIdQuery(
        contact_id=contact_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
    )
    contact = await mediator.handle_query(query)

    return ApiResponse[ContactResponseSchema](
        data=ContactResponseSchema.from_entity(contact),
    )


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Contact deleted successfully"},
        status.HTTP_409_CONFLICT: {"description": "Contact has active deals"},
    },
)
async def delete_contact(
    contact_id: UUID,
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    member: OrganizationMemberEntity = Depends(get_organization_member),
    container=Depends(init_container),
) -> None:
    """Удалить контакт."""
    mediator: Mediator = container.resolve(Mediator)

    role = member.role.as_generic_type()
    command = DeleteContactCommand(
        contact_id=contact_id,
        organization_id=organization_id,
        user_id=user_id,
        user_role=role.value,
    )
    await mediator.handle_command(command)
