from uuid import uuid4

from domain.sales.entities import ActivityEntity
from domain.sales.value_objects.activities import (
    ActivityPayloadValueObject,
    ActivityTypeValueObject,
)


def test_activity_entity_creation():
    deal_id = uuid4()
    author_id = uuid4()

    activity = ActivityEntity(
        deal_id=deal_id,
        author_user_id=author_id,
        type=ActivityTypeValueObject("comment"),
        payload=ActivityPayloadValueObject({"text": "Hello"}),
    )

    assert activity.deal_id == deal_id
    assert activity.author_user_id == author_id
    assert activity.type.as_generic_type().value == "comment"
    assert activity.payload.as_generic_type() == {"text": "Hello"}
    assert activity.oid is not None
    assert activity.created_at is not None


def test_activity_entity_without_author():
    deal_id = uuid4()

    activity = ActivityEntity(
        deal_id=deal_id,
        author_user_id=None,
        type=ActivityTypeValueObject("status_changed"),
        payload=ActivityPayloadValueObject({"old_status": "new", "new_status": "won"}),
    )

    assert activity.deal_id == deal_id
    assert activity.author_user_id is None
    assert activity.type.as_generic_type().value == "status_changed"


def test_activity_entity_equality():
    activity_id = uuid4()
    deal_id = uuid4()

    activity1 = ActivityEntity(
        oid=activity_id,
        deal_id=deal_id,
        author_user_id=None,
        type=ActivityTypeValueObject("system"),
        payload=ActivityPayloadValueObject({"event": "created"}),
    )
    activity2 = ActivityEntity(
        oid=activity_id,
        deal_id=deal_id,
        author_user_id=None,
        type=ActivityTypeValueObject("system"),
        payload=ActivityPayloadValueObject({"event": "created"}),
    )

    assert activity1 == activity2
    assert hash(activity1) == hash(activity2)
