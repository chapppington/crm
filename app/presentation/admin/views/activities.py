from infrastructure.database.models.sales.activity import ActivityModel
from starlette_admin.contrib.sqla import ModelView


class ActivityView(ModelView):
    def __init__(self):
        super().__init__(
            model=ActivityModel,
            name="Действия",
            label="Действия",
            icon="fa-solid fa-clock",
        )

    fields = [
        "oid",
        "deal_id",
        "author_id",
        "type",
        "payload",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["type", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["type"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
