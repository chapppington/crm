from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.sales.commands import (
    CreateContactCommand,
    CreateDealCommand,
    DeleteContactCommand,
)
from application.sales.queries import GetContactByIdQuery
from domain.sales.entities import ContactEntity
from domain.sales.exceptions.sales import (
    ContactHasActiveDealsException,
    ContactNotFoundException,
    EmptyContactNameException,
)


@pytest.mark.asyncio
async def test_create_contact_command_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    contact_name = faker.name()
    contact_email = faker.email()
    contact_phone = f"+7{faker.numerify('##########')}"

    result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=contact_name,
            email=contact_email,
            phone=contact_phone,
        ),
    )

    contact: ContactEntity = result

    assert contact is not None
    assert contact.name.as_generic_type() == contact_name
    assert contact.email.as_generic_type() == contact_email
    assert contact.phone.as_generic_type() == contact_phone
    assert contact.organization_id == organization_id
    assert contact.owner_user_id == owner_user_id
    assert contact.oid is not None

    retrieved_contact = await mediator.handle_query(
        GetContactByIdQuery(contact_id=contact.oid),
    )

    assert retrieved_contact.oid == contact.oid
    assert retrieved_contact.name.as_generic_type() == contact_name


@pytest.mark.asyncio
async def test_create_contact_command_empty_name(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()

    with pytest.raises(EmptyContactNameException):
        await mediator.handle_command(
            CreateContactCommand(
                organization_id=organization_id,
                owner_user_id=owner_user_id,
                name="",
            ),
        )


@pytest.mark.asyncio
async def test_create_contact_command_without_email_and_phone(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    owner_user_id = uuid4()
    contact_name = faker.name()

    result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            name=contact_name,
        ),
    )

    contact: ContactEntity = result

    assert contact.name.as_generic_type() == contact_name
    assert contact.email.as_generic_type() is None
    assert contact.phone.as_generic_type() is None


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
async def test_delete_contact_command_success(
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

    await mediator.handle_command(DeleteContactCommand(contact_id=contact_id))

    with pytest.raises(ContactNotFoundException):
        await mediator.handle_query(
            GetContactByIdQuery(contact_id=contact_id),
        )


@pytest.mark.asyncio
async def test_delete_contact_with_active_deals_fails(
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

    with pytest.raises(ContactHasActiveDealsException) as exc_info:
        await mediator.handle_command(DeleteContactCommand(contact_id=contact_id))

    assert exc_info.value.contact_id == contact_id
