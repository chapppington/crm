from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.organizations.queries import GetOrganizationByIdQuery
from domain.organizations.entities import OrganizationEntity
from domain.organizations.exceptions.organizations import (
    EmptyOrganizationNameException,
    OrganizationNotFoundException,
)


@pytest.mark.asyncio
async def test_create_organization_command_success(
    mediator: Mediator,
    faker: Faker,
):
    organization_name = faker.company()

    result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=organization_name),
    )

    organization: OrganizationEntity = result

    assert organization is not None
    assert organization.name.as_generic_type() == organization_name
    assert organization.oid is not None

    # Проверяем, что организацию можно получить по ID
    retrieved_organization = await mediator.handle_query(
        GetOrganizationByIdQuery(organization_id=organization.oid),
    )

    assert retrieved_organization.oid == organization.oid
    assert retrieved_organization.name.as_generic_type() == organization_name


@pytest.mark.asyncio
async def test_create_organization_command_empty_name(
    mediator: Mediator,
):
    with pytest.raises(EmptyOrganizationNameException):
        await mediator.handle_command(
            CreateOrganizationCommand(name=""),
        )


@pytest.mark.asyncio
async def test_get_organization_by_id_not_found(
    mediator: Mediator,
):
    non_existent_id = uuid4()

    with pytest.raises(OrganizationNotFoundException) as exc_info:
        await mediator.handle_query(
            GetOrganizationByIdQuery(organization_id=non_existent_id),
        )

    assert exc_info.value.organization_id == non_existent_id


@pytest.mark.asyncio
async def test_create_multiple_organizations(
    mediator: Mediator,
    faker: Faker,
):
    organization1_name = faker.company()
    organization2_name = faker.company()

    result1, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=organization1_name),
    )
    result2, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=organization2_name),
    )

    org1: OrganizationEntity = result1
    org2: OrganizationEntity = result2

    assert org1.oid != org2.oid
    assert org1.name.as_generic_type() == organization1_name
    assert org2.name.as_generic_type() == organization2_name

    retrieved_org1 = await mediator.handle_query(
        GetOrganizationByIdQuery(organization_id=org1.oid),
    )
    retrieved_org2 = await mediator.handle_query(
        GetOrganizationByIdQuery(organization_id=org2.oid),
    )

    assert retrieved_org1.name.as_generic_type() == organization1_name
    assert retrieved_org2.name.as_generic_type() == organization2_name
