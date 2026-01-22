from uuid import UUID

from starlette.requests import Request
from starlette.responses import Response

from presentation.api.auth import auth_service
from starlette_admin.auth import (
    AdminConfig,
    AdminUser,
    AuthProvider,
)
from starlette_admin.exceptions import (
    FormValidationError,
    LoginFailed,
)

from application.container import init_container
from application.mediator import Mediator
from application.users.queries import (
    AuthenticateUserQuery,
    GetUserByIdQuery,
)
from domain.users.exceptions import InvalidCredentialsException


class JWTAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if not username or not password:
            raise FormValidationError({"username": "Email и пароль обязательны для заполнения"})

        container = init_container()
        mediator: Mediator = container.resolve(Mediator)

        try:
            query = AuthenticateUserQuery(
                email=username,
                password=password,
            )

            user = await mediator.handle_query(query)

            user_id = str(user.oid)
            access_token = auth_service.create_access_token(uid=user_id)
            refresh_token = auth_service.create_refresh_token(uid=user_id)

            from starlette.responses import RedirectResponse

            next_url = request.query_params.get("next", "/admin/")
            redirect_response = RedirectResponse(url=next_url, status_code=303)

            auth_service.set_access_cookies(token=access_token, response=redirect_response)
            auth_service.set_refresh_cookies(token=refresh_token, response=redirect_response)

            return redirect_response

        except InvalidCredentialsException:
            raise LoginFailed("Неверный email или пароль")
        except Exception:
            raise LoginFailed("Неверный email или пароль")

    async def is_authenticated(self, request: Request) -> bool:
        try:
            token_payload = await auth_service.access_token_required(request)

            user_id_str = getattr(token_payload, "sub", None)
            if not user_id_str:
                return False

            user_id = UUID(user_id_str)

            container = init_container()
            mediator: Mediator = container.resolve(Mediator)

            query = GetUserByIdQuery(user_id=user_id)
            user = await mediator.handle_query(query)

            request.state.user = {
                "id": str(user.oid),
                "email": user.email.as_generic_type(),
                "name": user.name.as_generic_type(),
            }

            return True

        except Exception:
            return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user
        custom_app_title = f"CRM Admin - {user['name']}"
        return AdminConfig(app_title=custom_app_title)

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(
            username=user["name"],
            photo_url=None,
        )

    async def logout(self, request: Request, response: Response) -> Response:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response
