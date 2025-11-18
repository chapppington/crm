from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.organizations.queries import GetOrganizationByIdQuery
from domain.organizations.entities import OrganizationEntity
from domain.organizations.exceptions.organizations import OrganizationNotFoundException


@pytest.mark.asyncio
async def test_get_organization_by_id_success(
    mediator: Mediator,
    faker: Faker,
):
    organization_name = faker.company()

    result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=organization_name),
    )
    created_org: OrganizationEntity = result

    retrieved_org = await mediator.handle_query(
        GetOrganizationByIdQuery(organization_id=created_org.oid),
    )

    assert retrieved_org.oid == created_org.oid
    assert retrieved_org.name.as_generic_type() == organization_name


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
