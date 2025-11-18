from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.sales.commands import CreateContactCommand
from application.sales.queries import (
    GetContactByIdQuery,
    GetContactsQuery,
)
from domain.sales.entities import ContactEntity
from domain.sales.exceptions.sales import ContactNotFoundException
from domain.sales.filters import ContactFilters


@pytest.mark.asyncio
async def test_get_contact_by_id_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()
    contact_name = faker.name()

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=contact_name,
        ),
    )
    created_contact: ContactEntity = contact_result

    retrieved_contact = await mediator.handle_query(
        GetContactByIdQuery(contact_id=created_contact.oid),
    )

    assert retrieved_contact.oid == created_contact.oid
    assert retrieved_contact.name.as_generic_type() == contact_name
    assert retrieved_contact.organization_id == organization_id


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(
    mediator: Mediator,
):
    non_existent_id = uuid4()

    with pytest.raises(ContactNotFoundException) as exc_info:
        await mediator.handle_query(
            GetContactByIdQuery(contact_id=non_existent_id),
        )

    assert exc_info.value.contact_id == non_existent_id


@pytest.mark.asyncio
async def test_get_contacts_query_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact1_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )

    contact2_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=faker.name(),
        ),
    )

    filters = ContactFilters(organization_id=organization_id)
    contacts, count = await mediator.handle_query(GetContactsQuery(filters=filters))

    contacts_list = list(contacts)
    assert count >= 2
    assert len(contacts_list) >= 2

    contact_ids = [c.oid for c in contacts_list]
    assert contact1_result.oid in contact_ids
    assert contact2_result.oid in contact_ids


@pytest.mark.asyncio
async def test_get_contacts_query_with_search_filter(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    search_name = "TestContact"
    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=search_name,
        ),
    )

    filters = ContactFilters(organization_id=organization_id, search=search_name)
    contacts, count = await mediator.handle_query(GetContactsQuery(filters=filters))

    contacts_list = list(contacts)
    assert count >= 1
    assert any(c.oid == contact_result.oid for c in contacts_list)


@pytest.mark.asyncio
async def test_get_contacts_query_with_pagination(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    for _ in range(3):
        await mediator.handle_command(
            CreateContactCommand(
                organization_id=organization_id,
                owner_user_id=owner_user_id,
                name=faker.name(),
            ),
        )

    filters = ContactFilters(organization_id=organization_id, page=1, page_size=2)
    contacts, count = await mediator.handle_query(GetContactsQuery(filters=filters))

    contacts_list = list(contacts)
    assert count >= 3
    assert len(contacts_list) <= 2
