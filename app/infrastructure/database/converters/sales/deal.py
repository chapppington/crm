from infrastructure.database.models.sales.deal import DealModel

from domain.sales.entities.deals import DealEntity
from domain.sales.value_objects.deals import (
    CurrencyValueObject,
    DealAmountValueObject,
    DealStageValueObject,
    DealStatusValueObject,
    DealTitleValueObject,
)


def deal_entity_to_model(entity: DealEntity) -> DealModel:
    return DealModel(
        oid=entity.oid,
        organization_id=entity.organization_id,
        contact_id=entity.contact_id,
        owner_id=entity.owner_user_id,
        title=entity.title.as_generic_type(),
        amount=entity.amount.as_generic_type(),
        currency=entity.currency.as_generic_type(),
        status=entity.status.as_generic_type().value,
        stage=entity.stage.as_generic_type().value,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def deal_model_to_entity(model: DealModel) -> DealEntity:
    return DealEntity(
        oid=model.oid,
        organization_id=model.organization_id,
        contact_id=model.contact_id,
        owner_user_id=model.owner_id,
        title=DealTitleValueObject(value=model.title),
        amount=DealAmountValueObject(value=float(model.amount)),
        currency=CurrencyValueObject(value=model.currency),
        status=DealStatusValueObject(value=model.status),
        stage=DealStageValueObject(value=model.stage),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
