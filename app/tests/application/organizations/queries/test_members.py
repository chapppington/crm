from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    CreateOrganizationCommand,
)
from application.organizations.queries import (
    GetMemberByOrganizationAndUserQuery,
    GetUserOrganizationsQuery,
)
from domain.organizations.entities import OrganizationMemberEntity
from domain.organizations.exceptions.members import UserNotMemberOfOrganizationException


@pytest.mark.asyncio
async def test_get_member_by_organization_and_user_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    user_id = uuid4()
    role = "member"

    member_result, *_ = await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        ),
    )
    created_member: OrganizationMemberEntity = member_result

    retrieved_member = await mediator.handle_query(
        GetMemberByOrganizationAndUserQuery(
            organization_id=organization_id,
            user_id=user_id,
        ),
    )

    assert retrieved_member.oid == created_member.oid
    assert retrieved_member.organization_id == organization_id
    assert retrieved_member.user_id == user_id
    assert retrieved_member.role.as_generic_type().value == role


@pytest.mark.asyncio
async def test_get_member_by_organization_and_user_not_found(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    user_id = uuid4()

    with pytest.raises(UserNotMemberOfOrganizationException) as exc_info:
        await mediator.handle_query(
            GetMemberByOrganizationAndUserQuery(
                organization_id=organization_id,
                user_id=user_id,
            ),
        )

    assert exc_info.value.organization_id == organization_id
    assert exc_info.value.user_id == user_id


@pytest.mark.asyncio
async def test_get_user_organizations_success(
    mediator: Mediator,
    faker: Faker,
):
    user_id = uuid4()

    org1_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    org2_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=org1_result.oid,
            user_id=user_id,
            role="member",
        ),
    )

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=org2_result.oid,
            user_id=user_id,
            role="admin",
        ),
    )

    members, organizations_map = await mediator.handle_query(
        GetUserOrganizationsQuery(user_id=user_id),
    )

    members_list = list(members)
    assert len(members_list) == 2

    org_ids = [m.organization_id for m in members_list]
    assert org1_result.oid in org_ids
    assert org2_result.oid in org_ids

    for member in members_list:
        assert member.user_id == user_id

    assert isinstance(organizations_map, dict)
    assert len(organizations_map) >= 0


@pytest.mark.asyncio
async def test_get_user_organizations_empty(
    mediator: Mediator,
):
    user_id = uuid4()

    members, organizations_map = await mediator.handle_query(
        GetUserOrganizationsQuery(user_id=user_id),
    )

    members_list = list(members)
    assert len(members_list) == 0
    assert isinstance(organizations_map, dict)
    assert len(organizations_map) == 0
