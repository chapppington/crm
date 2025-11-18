from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.responses import JSONResponse

from presentation.api.schemas import ApiResponse

from application.base.exception import LogicException
from domain.base.exceptions import (
    ApplicationException,
    DomainException,
)
from domain.organizations.exceptions import OrganizationException
from domain.sales.exceptions import SalesException
from domain.users.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserException,
    UserNotFoundException,
)


async def application_exception_handler(
    request: Request,
    exc: ApplicationException,
) -> JSONResponse:
    if isinstance(exc, LogicException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, DomainException):
        if isinstance(exc, UserException):
            if isinstance(exc, (InvalidCredentialsException, UserNotFoundException)):
                status_code = status.HTTP_401_UNAUTHORIZED
            elif isinstance(exc, UserAlreadyExistsException):
                status_code = status.HTTP_409_CONFLICT
            else:
                status_code = status.HTTP_400_BAD_REQUEST
        elif isinstance(exc, (SalesException, OrganizationException)):
            if "NotFound" in exc.__class__.__name__ or "ResourceNotFound" in exc.__class__.__name__:
                status_code = status.HTTP_404_NOT_FOUND
            elif (
                "Mismatch" in exc.__class__.__name__
                or "NotAllowed" in exc.__class__.__name__
                or "AccessDenied" in exc.__class__.__name__
            ):
                status_code = status.HTTP_403_FORBIDDEN
            else:
                status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    response = ApiResponse(
        errors=[{"message": exc.message, "type": exc.__class__.__name__}],
    )

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    response = ApiResponse(
        errors=[{"message": str(exc), "type": exc.__class__.__name__}],
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        ApplicationException,
        application_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        general_exception_handler,
    )
