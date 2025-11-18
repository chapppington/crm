from datetime import (
    date,
    timedelta,
)
from uuid import uuid4

import pytest
from faker import Faker

from application.mediator import Mediator
from application.organizations.commands import CreateOrganizationCommand
from application.sales.commands import (
    CreateContactCommand,
    CreateDealCommand,
    CreateTaskCommand,
    UpdateTaskCommand,
)
from application.sales.queries import GetTaskByIdQuery
from domain.sales.entities import TaskEntity
from domain.sales.exceptions.sales import (
    EmptyTaskTitleException,
    InvalidTaskDueDateException,
)


@pytest.mark.asyncio
async def test_create_task_command_success(
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

    task_title = faker.sentence()
    task_description = faker.text()
    task_due_date = date.today() + timedelta(days=1)

    result, *_ = await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal_id,
            title=task_title,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=task_description,
            due_date=task_due_date,
        ),
    )

    task: TaskEntity = result

    assert task is not None
    assert task.title.as_generic_type() == task_title
    assert task.description.as_generic_type() == task_description
    assert task.due_date.as_generic_type() == task_due_date
    assert task.deal_id == deal_id
    assert task.is_done is False
    assert task.oid is not None

    retrieved_task = await mediator.handle_query(
        GetTaskByIdQuery(
            task_id=task.oid,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    assert retrieved_task.oid == task.oid
    assert retrieved_task.title.as_generic_type() == task_title


@pytest.mark.asyncio
async def test_create_task_command_empty_title(
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

    with pytest.raises(EmptyTaskTitleException):
        await mediator.handle_command(
            CreateTaskCommand(
                deal_id=deal_id,
                title="",
                organization_id=organization_id,
                user_id=owner_user_id,
                user_role="owner",
                description=faker.text(),
                due_date=date.today() + timedelta(days=1),
            ),
        )


@pytest.mark.asyncio
async def test_create_task_command_past_due_date(
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

    past_date = date.today() - timedelta(days=1)

    with pytest.raises(InvalidTaskDueDateException) as exc_info:
        await mediator.handle_command(
            CreateTaskCommand(
                deal_id=deal_id,
                title=faker.sentence(),
                organization_id=organization_id,
                user_id=owner_user_id,
                user_role="owner",
                description=faker.text(),
                due_date=past_date,
            ),
        )

    assert exc_info.value.due_date == past_date
    assert exc_info.value.today == date.today()


@pytest.mark.asyncio
async def test_create_task_command_today_due_date(
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

    today = date.today()

    result, *_ = await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal_id,
            title=faker.sentence(),
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=faker.text(),
            due_date=today,
        ),
    )

    task: TaskEntity = result
    assert task.due_date.as_generic_type() == today


@pytest.mark.asyncio
async def test_update_task_command_success(
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

    task_result, *_ = await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal_id,
            title=faker.sentence(),
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=faker.text(),
            due_date=date.today() + timedelta(days=1),
        ),
    )
    task_id = task_result.oid

    new_title = faker.sentence()
    new_description = faker.text()
    new_due_date = date.today() + timedelta(days=2)

    await mediator.handle_command(
        UpdateTaskCommand(
            task_id=task_id,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            title=new_title,
            description=new_description,
            due_date=new_due_date,
            is_done=True,
        ),
    )

    updated_task = await mediator.handle_query(
        GetTaskByIdQuery(
            task_id=task_id,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    assert updated_task.title.as_generic_type() == new_title
    assert updated_task.description.as_generic_type() == new_description
    assert updated_task.due_date.as_generic_type() == new_due_date
    assert updated_task.is_done is True
