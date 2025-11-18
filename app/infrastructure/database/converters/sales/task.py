from infrastructure.database.models.sales.task import TaskModel

from domain.sales.entities.tasks import TaskEntity
from domain.sales.value_objects.tasks import (
    TaskDescriptionValueObject,
    TaskDueDateValueObject,
    TaskTitleValueObject,
)


def task_entity_to_model(entity: TaskEntity) -> TaskModel:
    return TaskModel(
        oid=entity.oid,
        deal_id=entity.deal_id,
        title=entity.title.as_generic_type(),
        description=entity.description.as_generic_type(),
        due_date=entity.due_date.as_generic_type(),
        is_done=entity.is_done,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def task_model_to_entity(model: TaskModel) -> TaskEntity:
    return TaskEntity(
        oid=model.oid,
        deal_id=model.deal_id,
        title=TaskTitleValueObject(value=model.title),
        description=TaskDescriptionValueObject(value=model.description),
        due_date=TaskDueDateValueObject(value=model.due_date),
        is_done=model.is_done,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
