from infrastructure.database.models.sales.deal import DealModel
from starlette_admin.contrib.sqla import ModelView


class DealView(ModelView):
    def __init__(self):
        super().__init__(
            model=DealModel,
            name="Сделки",
            label="Сделки",
            icon="fa-solid fa-handshake",
        )

    fields = [
        "oid",
        "organization_id",
        "contact_id",
        "owner_id",
        "title",
        "amount",
        "currency",
        "status",
        "stage",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["title", "amount", "status", "stage", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["title", "status", "stage"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
