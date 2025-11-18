from datetime import date
from uuid import uuid4

from domain.sales.entities import TaskEntity
from domain.sales.value_objects.tasks import (
    TaskDescriptionValueObject,
    TaskDueDateValueObject,
    TaskTitleValueObject,
)


def test_task_entity_creation():
    deal_id = uuid4()
    due_date = date.today()

    task = TaskEntity(
        deal_id=deal_id,
        title=TaskTitleValueObject("Call client"),
        description=TaskDescriptionValueObject("Discuss proposal"),
        due_date=TaskDueDateValueObject(due_date),
        is_done=False,
    )

    assert task.deal_id == deal_id
    assert task.title.as_generic_type() == "Call client"
    assert task.description.as_generic_type() == "Discuss proposal"
    assert task.due_date.as_generic_type() == due_date
    assert task.is_done is False
    assert task.oid is not None
    assert task.created_at is not None


def test_task_entity_default_is_done():
    deal_id = uuid4()

    task = TaskEntity(
        deal_id=deal_id,
        title=TaskTitleValueObject("Task"),
        description=TaskDescriptionValueObject(None),
        due_date=TaskDueDateValueObject(None),
    )

    assert task.is_done is False


def test_task_entity_equality():
    task_id = uuid4()
    deal_id = uuid4()

    task1 = TaskEntity(
        oid=task_id,
        deal_id=deal_id,
        title=TaskTitleValueObject("Task"),
        description=TaskDescriptionValueObject("Description"),
        due_date=TaskDueDateValueObject(date.today()),
    )
    task2 = TaskEntity(
        oid=task_id,
        deal_id=deal_id,
        title=TaskTitleValueObject("Task"),
        description=TaskDescriptionValueObject("Description"),
        due_date=TaskDueDateValueObject(date.today()),
    )

    assert task1 == task2
    assert hash(task1) == hash(task2)
