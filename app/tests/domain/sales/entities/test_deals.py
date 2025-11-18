from uuid import uuid4

from domain.sales.entities import DealEntity
from domain.sales.value_objects.deals import (
    CurrencyValueObject,
    DealAmountValueObject,
    DealStageValueObject,
    DealStatusValueObject,
    DealTitleValueObject,
)


def test_deal_entity_creation():
    org_id = uuid4()
    contact_id = uuid4()
    user_id = uuid4()

    deal = DealEntity(
        organization_id=org_id,
        contact_id=contact_id,
        owner_user_id=user_id,
        title=DealTitleValueObject("Website Redesign"),
        amount=DealAmountValueObject(10000.0),
        currency=CurrencyValueObject("USD"),
        status=DealStatusValueObject("new"),
        stage=DealStageValueObject("qualification"),
    )

    assert deal.organization_id == org_id
    assert deal.contact_id == contact_id
    assert deal.owner_user_id == user_id
    assert deal.title.as_generic_type() == "Website Redesign"
    assert deal.amount.as_generic_type() == 10000.0
    assert deal.currency.as_generic_type() == "USD"
    assert deal.status.as_generic_type().value == "new"
    assert deal.stage.as_generic_type().value == "qualification"
    assert deal.oid is not None
    assert deal.created_at is not None


def test_deal_entity_equality():
    deal_id = uuid4()
    org_id = uuid4()
    contact_id = uuid4()
    user_id = uuid4()

    deal1 = DealEntity(
        oid=deal_id,
        organization_id=org_id,
        contact_id=contact_id,
        owner_user_id=user_id,
        title=DealTitleValueObject("Deal 1"),
        amount=DealAmountValueObject(5000.0),
        currency=CurrencyValueObject("EUR"),
        status=DealStatusValueObject("in_progress"),
        stage=DealStageValueObject("proposal"),
    )
    deal2 = DealEntity(
        oid=deal_id,
        organization_id=org_id,
        contact_id=contact_id,
        owner_user_id=user_id,
        title=DealTitleValueObject("Deal 1"),
        amount=DealAmountValueObject(5000.0),
        currency=CurrencyValueObject("EUR"),
        status=DealStatusValueObject("in_progress"),
        stage=DealStageValueObject("proposal"),
    )

    assert deal1 == deal2
    assert hash(deal1) == hash(deal2)
