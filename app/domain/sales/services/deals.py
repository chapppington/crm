from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from domain.sales.entities import DealEntity
from domain.sales.exceptions.sales import (
    CannotCloseDealWithZeroAmountException,
    DealNotFoundException,
)
from domain.sales.filters import DealFilters
from domain.sales.interfaces.repositories import BaseDealRepository
from domain.sales.value_objects.deals import (
    CurrencyValueObject,
    DealAmountValueObject,
    DealStage,
    DealStageValueObject,
    DealStatus,
    DealStatusValueObject,
    DealTitleValueObject,
)


@dataclass
class DealService:
    deal_repository: BaseDealRepository

    async def create_deal(
        self,
        organization_id: UUID,
        contact_id: UUID,
        owner_user_id: UUID,
        title: str,
        amount: float,
        currency: str,
    ) -> DealEntity:
        deal = DealEntity(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=DealTitleValueObject(title),
            amount=DealAmountValueObject(amount),
            currency=CurrencyValueObject(currency),
            status=DealStatusValueObject(DealStatus.NEW.value),
            stage=DealStageValueObject(DealStage.QUALIFICATION.value),
        )
        await self.deal_repository.add(deal)
        return deal

    async def get_deal_by_id(
        self,
        deal_id: UUID,
    ) -> DealEntity:
        deal = await self.deal_repository.get_by_id(deal_id)
        if not deal:
            raise DealNotFoundException(deal_id=deal_id)
        return deal

    async def update_deal_status(
        self,
        deal_id: UUID,
        new_status: str,
    ) -> tuple[DealEntity, DealStatus | None]:
        deal = await self.get_deal_by_id(deal_id)
        old_status = deal.status.as_generic_type()
        new_status_vo = DealStatusValueObject(new_status)
        new_status_enum = new_status_vo.as_generic_type()

        if new_status_enum == DealStatus.WON:
            if deal.amount.as_generic_type() <= 0:
                raise CannotCloseDealWithZeroAmountException(deal_id=deal_id)

        deal.status = new_status_vo
        await self.deal_repository.update(deal)
        return deal, old_status

    async def update_deal_stage(
        self,
        deal_id: UUID,
        new_stage: str,
    ) -> tuple[DealEntity, DealStage | None]:
        deal = await self.get_deal_by_id(deal_id)
        old_stage = deal.stage.as_generic_type()
        new_stage_vo = DealStageValueObject(new_stage)

        deal.stage = new_stage_vo
        await self.deal_repository.update(deal)
        return deal, old_stage

    async def get_deal_list(
        self,
        filters: DealFilters,
    ) -> Iterable[DealEntity]:
        return await self.deal_repository.get_list(filters)

    async def get_deal_count(
        self,
        filters: DealFilters,
    ) -> int:
        return await self.deal_repository.get_count(filters)
