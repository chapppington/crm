from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    CreateOrganizationCommand,
)
from application.sales.commands import (
    CreateContactCommand,
    CreateDealCommand,
    UpdateDealStageCommand,
    UpdateDealStatusCommand,
)
from application.sales.queries import (
    GetActivitiesByDealIdQuery,
    GetDealByIdQuery,
)
from domain.sales.entities import DealEntity
from domain.sales.exceptions.sales import (
    AccessDeniedException,
    CannotCloseDealWithZeroAmountException,
    ContactOrganizationMismatchException,
    DealStageRollbackNotAllowedException,
    EmptyDealTitleException,
    InvalidDealAmountException,
)


@pytest.mark.asyncio
async def test_create_deal_command_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_title = faker.sentence()
    deal_amount = 10000.0
    deal_currency = "USD"

    result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=deal_title,
            amount=deal_amount,
            currency=deal_currency,
        ),
    )

    deal: DealEntity = result

    assert deal is not None
    assert deal.title.as_generic_type() == deal_title
    assert deal.amount.as_generic_type() == deal_amount
    assert deal.currency.as_generic_type() == deal_currency
    assert deal.organization_id == organization_id
    assert deal.contact_id == contact_id
    assert deal.owner_user_id == owner_user_id
    assert deal.oid is not None

    retrieved_deal = await mediator.handle_query(
        GetDealByIdQuery(
            deal_id=deal.oid,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    assert retrieved_deal.oid == deal.oid
    assert retrieved_deal.title.as_generic_type() == deal_title


@pytest.mark.asyncio
async def test_create_deal_command_empty_title(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    with pytest.raises(EmptyDealTitleException):
        await mediator.handle_command(
            CreateDealCommand(
                organization_id=organization_id,
                contact_id=contact_id,
                owner_user_id=owner_user_id,
                title="",
                amount=1000.0,
                currency="USD",
            ),
        )


@pytest.mark.asyncio
async def test_create_deal_command_negative_amount(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    with pytest.raises(InvalidDealAmountException) as exc_info:
        await mediator.handle_command(
            CreateDealCommand(
                organization_id=organization_id,
                contact_id=contact_id,
                owner_user_id=owner_user_id,
                title=faker.sentence(),
                amount=-100.0,
                currency="USD",
            ),
        )

    assert exc_info.value.amount == -100.0


@pytest.mark.asyncio
async def test_create_deal_command_contact_organization_mismatch(
    mediator: Mediator,
    faker: Faker,
):
    org1_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    org2_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=org1_result.oid,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    with pytest.raises(ContactOrganizationMismatchException) as exc_info:
        await mediator.handle_command(
            CreateDealCommand(
                organization_id=org2_result.oid,
                contact_id=contact_id,
                owner_user_id=owner_user_id,
                title=faker.sentence(),
                amount=1000.0,
                currency="USD",
            ),
        )

    assert exc_info.value.contact_id == contact_id
    assert exc_info.value.contact_organization_id == org1_result.oid
    assert exc_info.value.deal_organization_id == org2_result.oid


@pytest.mark.asyncio
async def test_update_deal_status_command_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    await mediator.handle_command(
        UpdateDealStatusCommand(
            deal_id=deal_id,
            new_status="won",
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    updated_deal = await mediator.handle_query(
        GetDealByIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    assert updated_deal.status.as_generic_type().value == "won"

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    activities_list = list(activities)
    assert len(activities_list) == 1
    assert activities_list[0].type.as_generic_type().value == "status_changed"
    assert activities_list[0].payload.as_generic_type()["old_status"] == "new"
    assert activities_list[0].payload.as_generic_type()["new_status"] == "won"


@pytest.mark.asyncio
async def test_update_deal_status_command_cannot_close_with_zero_amount(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=0.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    with pytest.raises(CannotCloseDealWithZeroAmountException) as exc_info:
        await mediator.handle_command(
            UpdateDealStatusCommand(
                deal_id=deal_id,
                new_status="won",
                organization_id=organization_id,
                user_id=owner_user_id,
                user_role="owner",
            ),
        )

    assert exc_info.value.deal_id == deal_id


@pytest.mark.asyncio
async def test_update_deal_stage_command_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    await mediator.handle_command(
        UpdateDealStageCommand(
            deal_id=deal_id,
            new_stage="proposal",
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="admin",
        ),
    )

    updated_deal = await mediator.handle_query(
        GetDealByIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    assert updated_deal.stage.as_generic_type().value == "proposal"

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    activities_list = list(activities)
    assert len(activities_list) == 1
    assert activities_list[0].type.as_generic_type().value == "stage_changed"
    assert activities_list[0].payload.as_generic_type()["old_stage"] == "qualification"
    assert activities_list[0].payload.as_generic_type()["new_stage"] == "proposal"


@pytest.mark.asyncio
async def test_update_deal_stage_command_rollback_not_allowed_for_member(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    await mediator.handle_command(
        UpdateDealStageCommand(
            deal_id=deal_id,
            new_stage="proposal",
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="admin",
        ),
    )

    with pytest.raises(DealStageRollbackNotAllowedException) as exc_info:
        await mediator.handle_command(
            UpdateDealStageCommand(
                deal_id=deal_id,
                new_stage="qualification",
                organization_id=organization_id,
                user_id=owner_user_id,
                user_role="member",
            ),
        )

    assert exc_info.value.deal_id == deal_id
    assert exc_info.value.current_stage == "proposal"
    assert exc_info.value.new_stage == "qualification"


@pytest.mark.asyncio
async def test_update_deal_status_command_member_cannot_update_other_user_deal(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()
    member_user_id = uuid4()

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=member_user_id,
            role="member",
        ),
    )

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    with pytest.raises(AccessDeniedException) as exc_info:
        await mediator.handle_command(
            UpdateDealStatusCommand(
                deal_id=deal_id,
                new_status="won",
                organization_id=organization_id,
                user_id=member_user_id,
                user_role="member",
            ),
        )

    assert exc_info.value.resource_type == "Deal"
    assert exc_info.value.resource_id == deal_id
    assert exc_info.value.user_id == member_user_id


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["owner", "admin", "manager"])
async def test_update_deal_status_command_owner_admin_manager_can_update_any_deal(
    mediator: Mediator,
    faker: Faker,
    role: str,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    deal_owner_user_id = uuid4()
    admin_user_id = uuid4()

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=admin_user_id,
            role=role,
        ),
    )

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=deal_owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=deal_owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    await mediator.handle_command(
        UpdateDealStatusCommand(
            deal_id=deal_id,
            new_status="won",
            organization_id=organization_id,
            user_id=admin_user_id,
            user_role=role,
        ),
    )

    updated_deal = await mediator.handle_query(
        GetDealByIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=admin_user_id,
            user_role=role,
        ),
    )

    assert updated_deal.status.as_generic_type().value == "won"


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["owner", "admin", "manager"])
async def test_update_deal_stage_command_owner_admin_manager_can_rollback_stage(
    mediator: Mediator,
    faker: Faker,
    role: str,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    deal_owner_user_id = uuid4()
    admin_user_id = uuid4()

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=admin_user_id,
            role=role,
        ),
    )

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=deal_owner_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=deal_owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    await mediator.handle_command(
        UpdateDealStageCommand(
            deal_id=deal_id,
            new_stage="proposal",
            organization_id=organization_id,
            user_id=deal_owner_user_id,
            user_role="owner",
        ),
    )

    await mediator.handle_command(
        UpdateDealStageCommand(
            deal_id=deal_id,
            new_stage="qualification",
            organization_id=organization_id,
            user_id=admin_user_id,
            user_role=role,
        ),
    )

    updated_deal = await mediator.handle_query(
        GetDealByIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=admin_user_id,
            user_role=role,
        ),
    )

    assert updated_deal.stage.as_generic_type().value == "qualification"


@pytest.mark.asyncio
async def test_update_deal_status_command_member_can_update_own_deal(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    member_user_id = uuid4()

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=member_user_id,
            role="member",
        ),
    )

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=member_user_id,
            name=faker.name(),
        ),
    )
    contact_id = contact_result.oid

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=member_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    deal_id = deal_result.oid

    await mediator.handle_command(
        UpdateDealStatusCommand(
            deal_id=deal_id,
            new_status="won",
            organization_id=organization_id,
            user_id=member_user_id,
            user_role="member",
        ),
    )

    updated_deal = await mediator.handle_query(
        GetDealByIdQuery(
            deal_id=deal_id,
            organization_id=organization_id,
            user_id=member_user_id,
            user_role="member",
        ),
    )

    assert updated_deal.status.as_generic_type().value == "won"
