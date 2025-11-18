from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.sales.commands import (
    CreateActivityCommand,
    CreateCommentActivityCommand,
    CreateContactCommand,
    CreateDealCommand,
)
from application.sales.queries import GetActivitiesByDealIdQuery


@pytest.mark.asyncio
async def test_get_activities_by_deal_id_success(
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

    activity1_result, *_ = await mediator.handle_command(
        CreateActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            activity_type="system",
            payload={"message": "Deal created"},
        ),
    )

    activity2_result, *_ = await mediator.handle_command(
        CreateCommentActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            text=faker.text(),
        ),
    )

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(deal_id=deal_id),
    )

    activities_list = list(activities)
    assert len(activities_list) >= 2

    activity_ids = [a.oid for a in activities_list]
    assert activity1_result.oid in activity_ids
    assert activity2_result.oid in activity_ids


@pytest.mark.asyncio
async def test_get_activities_by_deal_id_empty(
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

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(deal_id=deal_id),
    )

    activities_list = list(activities)
    assert len(activities_list) == 0


@pytest.mark.asyncio
async def test_get_activities_by_deal_id_multiple_types(
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
        CreateActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            activity_type="status_changed",
            payload={"old_status": "new", "new_status": "in_progress"},
        ),
    )

    await mediator.handle_command(
        CreateActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            activity_type="stage_changed",
            payload={"old_stage": "qualification", "new_stage": "proposal"},
        ),
    )

    await mediator.handle_command(
        CreateCommentActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            text=faker.text(),
        ),
    )

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(deal_id=deal_id),
    )

    activities_list = list(activities)
    assert len(activities_list) >= 3

    activity_types = [a.type.as_generic_type().value for a in activities_list]
    assert "status_changed" in activity_types
    assert "stage_changed" in activity_types
    assert "comment" in activity_types
