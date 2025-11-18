from infrastructure.database.models.sales.activity import ActivityModel

from domain.sales.entities.activities import ActivityEntity
from domain.sales.value_objects.activities import (
    ActivityPayloadValueObject,
    ActivityTypeValueObject,
)


def activity_entity_to_model(entity: ActivityEntity) -> ActivityModel:
    return ActivityModel(
        oid=entity.oid,
        deal_id=entity.deal_id,
        author_id=entity.author_user_id,
        type=entity.type.as_generic_type().value,
        payload=entity.payload.as_generic_type(),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def activity_model_to_entity(model: ActivityModel) -> ActivityEntity:
    return ActivityEntity(
        oid=model.oid,
        deal_id=model.deal_id,
        author_user_id=model.author_id,
        type=ActivityTypeValueObject(value=model.type),
        payload=ActivityPayloadValueObject(value=model.payload),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
