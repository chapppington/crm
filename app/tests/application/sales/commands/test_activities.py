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
from domain.sales.entities import ActivityEntity
from domain.sales.exceptions.sales import (
    EmptyActivityTypeException,
    InvalidActivityTypeException,
)


@pytest.mark.asyncio
async def test_create_activity_command_success(
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

    activity_type = "system"
    payload = {"message": "Deal created"}

    result, *_ = await mediator.handle_command(
        CreateActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            activity_type=activity_type,
            payload=payload,
        ),
    )

    activity: ActivityEntity = result

    assert activity is not None
    assert activity.deal_id == deal_id
    assert activity.author_user_id == owner_user_id
    assert activity.type.as_generic_type().value == activity_type
    assert activity.payload.as_generic_type() == payload
    assert activity.oid is not None

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(deal_id=deal_id),
    )

    activities_list = list(activities)
    assert len(activities_list) >= 1
    assert any(a.oid == activity.oid for a in activities_list)


@pytest.mark.asyncio
async def test_create_activity_command_empty_type(
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

    with pytest.raises(EmptyActivityTypeException):
        await mediator.handle_command(
            CreateActivityCommand(
                deal_id=deal_id,
                author_user_id=owner_user_id,
                activity_type="",
                payload={"message": "Test"},
            ),
        )


@pytest.mark.asyncio
async def test_create_activity_command_invalid_type(
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

    with pytest.raises(InvalidActivityTypeException) as exc_info:
        await mediator.handle_command(
            CreateActivityCommand(
                deal_id=deal_id,
                author_user_id=owner_user_id,
                activity_type="invalid_type",
                payload={"message": "Test"},
            ),
        )

    assert exc_info.value.activity_type == "invalid_type"


@pytest.mark.asyncio
async def test_create_comment_activity_command_success(
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

    comment_text = faker.text()

    result, *_ = await mediator.handle_command(
        CreateCommentActivityCommand(
            deal_id=deal_id,
            author_user_id=owner_user_id,
            text=comment_text,
        ),
    )

    activity: ActivityEntity = result

    assert activity is not None
    assert activity.deal_id == deal_id
    assert activity.author_user_id == owner_user_id
    assert activity.type.as_generic_type().value == "comment"
    assert activity.payload.as_generic_type() == {"text": comment_text}
    assert activity.oid is not None

    activities = await mediator.handle_query(
        GetActivitiesByDealIdQuery(deal_id=deal_id),
    )

    activities_list = list(activities)
    assert len(activities_list) >= 1
    assert any(a.oid == activity.oid for a in activities_list)


@pytest.mark.asyncio
async def test_create_activity_command_without_author(
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

    result, *_ = await mediator.handle_command(
        CreateActivityCommand(
            deal_id=deal_id,
            author_user_id=None,
            activity_type="system",
            payload={"message": "System event"},
        ),
    )

    activity: ActivityEntity = result

    assert activity.author_user_id is None
    assert activity.type.as_generic_type().value == "system"
