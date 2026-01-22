from infrastructure.database.models.organizations.member import OrganizationMemberModel
from starlette_admin.contrib.sqla import ModelView


class OrganizationMemberView(ModelView):
    def __init__(self):
        super().__init__(
            model=OrganizationMemberModel,
            name="Участники организации",
            label="Участники организации",
            icon="fa-solid fa-users",
        )

    fields = [
        "oid",
        "organization_id",
        "user_id",
        "role",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["role", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["role"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
