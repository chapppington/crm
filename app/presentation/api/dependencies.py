from uuid import UUID

from fastapi import (
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)

from presentation.api.auth import auth_service

from application.container import init_container
from application.mediator import Mediator
from application.organizations.queries import GetMemberByOrganizationAndUserQuery
from domain.organizations.entities import OrganizationMemberEntity


async def get_refresh_token_payload(
    request: Request,
) -> dict:
    """Dependency для получения payload из refresh токена."""
    return await auth_service.refresh_token_required(request)


async def get_access_token_payload(
    request: Request,
) -> dict:
    """Dependency для получения payload из access токена."""
    return await auth_service.access_token_required(request)


async def get_current_user_id(
    token_payload: dict = Depends(get_access_token_payload),
) -> UUID:
    """Dependency для получения текущего user_id из токена."""
    user_id_str = token_payload.sub
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token payload",
        )
    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
        )


async def get_organization_id(
    x_organization_id: str = Header(
        ...,
        alias="X-Organization-Id",
        description="Organization ID for multi-tenant context",
    ),
) -> UUID:
    """Dependency для получения organization_id из заголовка X-Organization-
    Id."""
    try:
        return UUID(x_organization_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization ID format in X-Organization-Id header",
        )


async def get_organization_member(
    organization_id: UUID = Depends(get_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    container=Depends(init_container),
) -> OrganizationMemberEntity:
    """Dependency для проверки членства пользователя в организации и получения
    роли."""
    mediator: Mediator = container.resolve(Mediator)

    query = GetMemberByOrganizationAndUserQuery(
        organization_id=organization_id,
        user_id=user_id,
    )

    member = await mediator.handle_query(query)
    return member
