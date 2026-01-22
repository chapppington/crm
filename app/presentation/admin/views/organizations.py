from infrastructure.database.models.organizations.organization import OrganizationModel
from starlette_admin.contrib.sqla import ModelView


class OrganizationView(ModelView):
    def __init__(self):
        super().__init__(
            model=OrganizationModel,
            name="Организации",
            label="Организации",
            icon="fa-solid fa-building",
        )

    fields = [
        "oid",
        "name",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["name", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["name"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
