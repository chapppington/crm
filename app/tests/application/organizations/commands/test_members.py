from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    CreateOrganizationCommand,
)
from application.organizations.queries import GetMemberByOrganizationAndUserQuery
from domain.organizations.entities import OrganizationMemberEntity
from domain.organizations.exceptions.members import (
    EmptyOrganizationMemberRoleException,
    InvalidOrganizationMemberRoleException,
    OrganizationMemberAlreadyExistsException,
)


@pytest.mark.asyncio
async def test_add_member_command_success(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    user_id = uuid4()
    role = "member"

    result, *_ = await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        ),
    )

    member: OrganizationMemberEntity = result

    assert member is not None
    assert member.organization_id == organization_id
    assert member.user_id == user_id
    assert member.role.as_generic_type().value == role
    assert member.oid is not None

    retrieved_member = await mediator.handle_query(
        GetMemberByOrganizationAndUserQuery(
            organization_id=organization_id,
            user_id=user_id,
        ),
    )

    assert retrieved_member.oid == member.oid
    assert retrieved_member.organization_id == organization_id
    assert retrieved_member.user_id == user_id


@pytest.mark.asyncio
async def test_add_member_command_different_roles(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid

    roles = ["owner", "admin", "manager", "member"]

    for i, role in enumerate(roles):
        user_id = uuid4()
        result, *_ = await mediator.handle_command(
            AddMemberCommand(
                organization_id=organization_id,
                user_id=user_id,
                role=role,
            ),
        )

        member: OrganizationMemberEntity = result
        assert member.role.as_generic_type().value == role


@pytest.mark.asyncio
async def test_add_member_command_empty_role(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    user_id = uuid4()

    with pytest.raises(EmptyOrganizationMemberRoleException):
        await mediator.handle_command(
            AddMemberCommand(
                organization_id=organization_id,
                user_id=user_id,
                role="",
            ),
        )


@pytest.mark.asyncio
async def test_add_member_command_invalid_role(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    user_id = uuid4()

    with pytest.raises(InvalidOrganizationMemberRoleException) as exc_info:
        await mediator.handle_command(
            AddMemberCommand(
                organization_id=organization_id,
                user_id=user_id,
                role="invalid_role",
            ),
        )

    assert exc_info.value.role == "invalid_role"


@pytest.mark.asyncio
async def test_add_member_command_duplicate_member(
    mediator: Mediator,
    faker: Faker,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization_id = org_result.oid
    user_id = uuid4()
    role = "member"

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        ),
    )

    with pytest.raises(OrganizationMemberAlreadyExistsException) as exc_info:
        await mediator.handle_command(
            AddMemberCommand(
                organization_id=organization_id,
                user_id=user_id,
                role="admin",
            ),
        )

    assert exc_info.value.organization_id == organization_id
    assert exc_info.value.user_id == user_id
