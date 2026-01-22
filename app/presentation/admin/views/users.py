from infrastructure.database.models.users.user import UserModel
from starlette_admin import PasswordField
from starlette_admin.contrib.sqla import ModelView


class UserView(ModelView):
    def __init__(self):
        super().__init__(
            model=UserModel,
            name="Пользователи",
            label="Пользователи",
            icon="fa-solid fa-user",
        )

    fields = [
        "oid",
        "email",
        PasswordField(
            name="hashed_password",
            label="Пароль",
            required=True,
            exclude_from_list=True,
            exclude_from_detail=True,
        ),
        "name",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["email", "name", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["email", "name"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
