from dataclasses import dataclass
from uuid import UUID

from domain.base.entity import BaseEntity
from domain.sales.value_objects.deals import (
    CurrencyValueObject,
    DealAmountValueObject,
    DealStageValueObject,
    DealStatusValueObject,
    DealTitleValueObject,
)


@dataclass(eq=False)
class DealEntity(BaseEntity):
    organization_id: UUID
    contact_id: UUID
    owner_user_id: UUID
    title: DealTitleValueObject
    amount: DealAmountValueObject
    currency: CurrencyValueObject
    status: DealStatusValueObject
    stage: DealStageValueObject
