import pytest

from domain.sales.exceptions.sales import (
    EmptyActivityTypeException,
    InvalidActivityTypeException,
)
from domain.sales.value_objects.activity import (
    ActivityPayloadValueObject,
    ActivityType,
    ActivityTypeValueObject,
)


@pytest.mark.parametrize(
    "type_value,expected_type",
    [
        ("comment", ActivityType.COMMENT),
        ("status_changed", ActivityType.STATUS_CHANGED),
        ("stage_changed", ActivityType.STAGE_CHANGED),
        ("task_created", ActivityType.TASK_CREATED),
        ("system", ActivityType.SYSTEM),
    ],
)
def test_activity_type_valid(type_value, expected_type):
    activity_type = ActivityTypeValueObject(type_value)
    assert activity_type.as_generic_type() == expected_type


@pytest.mark.parametrize(
    "type_value,exception",
    [
        ("", EmptyActivityTypeException),
        ("invalid_type", InvalidActivityTypeException),
        ("comment_added", InvalidActivityTypeException),
    ],
)
def test_activity_type_invalid(type_value, exception):
    with pytest.raises(exception):
        ActivityTypeValueObject(type_value)


@pytest.mark.parametrize(
    "payload_value,expected",
    [
        ({"text": "Hello", "key": "value"}, {"text": "Hello", "key": "value"}),
        ({}, {}),
        ({"old_status": "new", "new_status": "won"}, {"old_status": "new", "new_status": "won"}),
    ],
)
def test_activity_payload_valid(payload_value, expected):
    payload = ActivityPayloadValueObject(payload_value)
    assert payload.as_generic_type() == expected


@pytest.mark.parametrize(
    "payload_value",
    [
        "not a dict",
        123,
        [],
        None,
    ],
)
def test_activity_payload_invalid(payload_value):
    with pytest.raises(ValueError, match="Activity payload must be a dictionary"):
        ActivityPayloadValueObject(payload_value)
