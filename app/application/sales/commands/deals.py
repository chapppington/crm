from dataclasses import dataclass
from uuid import UUID

from application.base.command import (
    BaseCommand,
    BaseCommandHandler,
)
from domain.organizations.value_objects.members import OrganizationMemberRole
from domain.sales.entities import DealEntity
from domain.sales.exceptions.sales import (
    ContactOrganizationMismatchException,
    DealStageRollbackNotAllowedException,
)
from domain.sales.services import (
    ActivityService,
    ContactService,
    DealService,
)
from domain.sales.value_objects.deals import (
    DealStage,
    DealStatus,
)


@dataclass(frozen=True)
class CreateDealCommand(BaseCommand):
    organization_id: UUID
    contact_id: UUID
    owner_user_id: UUID
    title: str
    amount: float
    currency: str


@dataclass(frozen=True)
class UpdateDealStatusCommand(BaseCommand):
    deal_id: UUID
    new_status: str


@dataclass(frozen=True)
class UpdateDealStageCommand(BaseCommand):
    deal_id: UUID
    new_stage: str
    user_role: OrganizationMemberRole


@dataclass(frozen=True)
class CreateDealCommandHandler(
    BaseCommandHandler[CreateDealCommand, DealEntity],
):
    deal_service: DealService
    contact_service: ContactService

    async def handle(self, command: CreateDealCommand) -> DealEntity:
        contact = await self.contact_service.get_contact_by_id(command.contact_id)

        if contact.organization_id != command.organization_id:
            raise ContactOrganizationMismatchException(
                contact_id=command.contact_id,
                contact_organization_id=contact.organization_id,
                deal_organization_id=command.organization_id,
            )

        result = await self.deal_service.create_deal(
            organization_id=command.organization_id,
            contact_id=command.contact_id,
            owner_user_id=command.owner_user_id,
            title=command.title,
            amount=command.amount,
            currency=command.currency,
        )
        return result


@dataclass(frozen=True)
class UpdateDealStatusCommandHandler(
    BaseCommandHandler[
        UpdateDealStatusCommand,
        tuple[DealEntity, DealStatus | None],
    ],
):
    deal_service: DealService
    activity_service: ActivityService

    async def handle(
        self,
        command: UpdateDealStatusCommand,
    ) -> tuple[DealEntity, DealStatus | None]:
        deal, old_status = await self.deal_service.update_deal_status(
            deal_id=command.deal_id,
            new_status=command.new_status,
        )

        if old_status is not None:
            old_status_str = old_status.value
            new_status_str = deal.status.as_generic_type().value
            if old_status_str != new_status_str:
                await self.activity_service.create_status_changed_activity(
                    deal_id=deal.oid,
                    old_status=old_status_str,
                    new_status=new_status_str,
                )

        return deal, old_status


@dataclass(frozen=True)
class UpdateDealStageCommandHandler(
    BaseCommandHandler[
        UpdateDealStageCommand,
        tuple[DealEntity, DealStage | None],
    ],
):
    deal_service: DealService
    activity_service: ActivityService

    def _is_stage_rollback(
        self,
        current_stage: DealStage,
        new_stage: DealStage,
    ) -> bool:
        stage_order = {
            DealStage.QUALIFICATION: 1,
            DealStage.PROPOSAL: 2,
            DealStage.NEGOTIATION: 3,
            DealStage.CLOSED: 4,
        }
        return stage_order.get(current_stage, 0) > stage_order.get(new_stage, 0)

    async def handle(
        self,
        command: UpdateDealStageCommand,
    ) -> tuple[DealEntity, DealStage | None]:
        deal = await self.deal_service.get_deal_by_id(command.deal_id)
        old_stage = deal.stage.as_generic_type()
        new_stage_enum = DealStage(command.new_stage)

        if old_stage != new_stage_enum:
            is_rollback = self._is_stage_rollback(old_stage, new_stage_enum)

            if is_rollback and command.user_role not in {
                OrganizationMemberRole.ADMIN,
                OrganizationMemberRole.OWNER,
            }:
                raise DealStageRollbackNotAllowedException(
                    deal_id=command.deal_id,
                    current_stage=old_stage.value,
                    new_stage=command.new_stage,
                )

        deal, old_stage = await self.deal_service.update_deal_stage(
            deal_id=command.deal_id,
            new_stage=command.new_stage,
        )

        if old_stage is not None:
            old_stage_str = old_stage.value
            new_stage_str = deal.stage.as_generic_type().value
            if old_stage_str != new_stage_str:
                await self.activity_service.create_stage_changed_activity(
                    deal_id=deal.oid,
                    old_stage=old_stage_str,
                    new_stage=new_stage_str,
                )

        return deal, old_stage
