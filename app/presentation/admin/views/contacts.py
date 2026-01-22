from infrastructure.database.models.sales.contact import ContactModel
from starlette_admin.contrib.sqla import ModelView


class ContactView(ModelView):
    def __init__(self):
        super().__init__(
            model=ContactModel,
            name="Контакты",
            label="Контакты",
            icon="fa-solid fa-address-card",
        )

    fields = [
        "oid",
        "organization_id",
        "owner_id",
        "name",
        "email",
        "phone",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["name", "email", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["name", "email", "phone"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
