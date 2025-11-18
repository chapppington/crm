from datetime import (
    date,
    timedelta,
)

import pytest

from domain.sales.exceptions.sales import (
    EmptyTaskDescriptionException,
    EmptyTaskTitleException,
    InvalidTaskDueDateException,
)
from domain.sales.value_objects.tasks import (
    TaskDescriptionValueObject,
    TaskDueDateValueObject,
    TaskTitleValueObject,
)


@pytest.mark.parametrize(
    "title_value,expected",
    [
        ("Call client", "Call client"),
        ("A" * 255, "A" * 255),
        ("Task #123", "Task #123"),
    ],
)
def test_task_title_valid(title_value, expected):
    title = TaskTitleValueObject(title_value)
    assert title.as_generic_type() == expected
    assert len(title.as_generic_type()) == len(expected)


@pytest.mark.parametrize(
    "title_value",
    [
        "",
        "A" * 256,
    ],
)
def test_task_title_invalid(title_value):
    with pytest.raises(EmptyTaskTitleException):
        TaskTitleValueObject(title_value)


@pytest.mark.parametrize(
    "description_value,expected",
    [
        ("Some description", "Some description"),
        (None, None),
    ],
)
def test_task_description_valid(description_value, expected):
    description = TaskDescriptionValueObject(description_value)
    assert description.as_generic_type() == expected


def test_task_description_empty_string():
    with pytest.raises(EmptyTaskDescriptionException):
        TaskDescriptionValueObject("")


@pytest.mark.parametrize(
    "due_date_value,expected",
    [
        (date.today(), date.today()),
        (date.today() + timedelta(days=7), date.today() + timedelta(days=7)),
        (None, None),
    ],
)
def test_task_due_date_valid(due_date_value, expected):
    due_date = TaskDueDateValueObject(due_date_value)
    assert due_date.as_generic_type() == expected


@pytest.mark.parametrize(
    "days_offset",
    [
        -1,
        -7,
        -365,
    ],
)
def test_task_due_date_past(days_offset):
    past_date = date.today() + timedelta(days=days_offset)
    with pytest.raises(InvalidTaskDueDateException):
        TaskDueDateValueObject(past_date)
