from fastapi import Request

from presentation.api.auth import auth_service


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
