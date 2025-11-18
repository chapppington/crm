from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.sales.commands import (
    CreateContactCommand,
    CreateDealCommand,
)
from application.sales.queries import (
    GetDealByIdQuery,
    GetDealsQuery,
)
from domain.sales.entities import DealEntity
from domain.sales.exceptions.sales import DealNotFoundException
from domain.sales.filters import DealFilters


@pytest.mark.asyncio
async def test_get_deal_by_id_success(
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
    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=deal_title,
            amount=1000.0,
            currency="USD",
        ),
    )
    created_deal: DealEntity = deal_result

    retrieved_deal = await mediator.handle_query(
        GetDealByIdQuery(deal_id=created_deal.oid),
    )

    assert retrieved_deal.oid == created_deal.oid
    assert retrieved_deal.title.as_generic_type() == deal_title
    assert retrieved_deal.organization_id == organization_id


@pytest.mark.asyncio
async def test_get_deal_by_id_not_found(
    mediator: Mediator,
):
    non_existent_id = uuid4()

    with pytest.raises(DealNotFoundException) as exc_info:
        await mediator.handle_query(
            GetDealByIdQuery(deal_id=non_existent_id),
        )

    assert exc_info.value.deal_id == non_existent_id


@pytest.mark.asyncio
async def test_get_deals_query_success(
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

    deal1_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )

    deal2_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_user_id=owner_user_id,
            title=faker.sentence(),
            amount=2000.0,
            currency="USD",
        ),
    )

    filters = DealFilters(organization_id=organization_id)
    deals, count = await mediator.handle_query(GetDealsQuery(filters=filters))

    deals_list = list(deals)
    assert count >= 2
    assert len(deals_list) >= 2

    deal_ids = [d.oid for d in deals_list]
    assert deal1_result.oid in deal_ids
    assert deal2_result.oid in deal_ids


@pytest.mark.asyncio
async def test_get_deals_query_with_pagination(
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

    for _ in range(3):
        await mediator.handle_command(
            CreateDealCommand(
                organization_id=organization_id,
                contact_id=contact_id,
                owner_user_id=owner_user_id,
                title=faker.sentence(),
                amount=1000.0,
                currency="USD",
            ),
        )

    filters = DealFilters(organization_id=organization_id, page=1, page_size=2)
    deals, count = await mediator.handle_query(GetDealsQuery(filters=filters))

    deals_list = list(deals)
    assert count >= 3
    assert len(deals_list) <= 2
