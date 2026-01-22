from infrastructure.database.models.sales.task import TaskModel
from starlette_admin.contrib.sqla import ModelView


class TaskView(ModelView):
    def __init__(self):
        super().__init__(
            model=TaskModel,
            name="Задачи",
            label="Задачи",
            icon="fa-solid fa-tasks",
        )

    fields = [
        "oid",
        "deal_id",
        "title",
        "description",
        "due_date",
        "is_done",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["created_at", "updated_at", "oid"]
    exclude_fields_from_create = ["created_at", "updated_at", "oid"]

    sortable_fields = ["title", "due_date", "is_done", "created_at"]
    fields_default_sort = [("created_at", True)]
    searchable_fields = ["title", "description"]

    page_size = 20
    page_size_options = [5, 10, 25, 50, -1]
