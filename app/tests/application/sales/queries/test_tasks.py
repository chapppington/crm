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
)
from application.sales.queries import (
    GetTaskByIdQuery,
    GetTasksQuery,
)
from domain.sales.entities import TaskEntity
from domain.sales.exceptions.sales import TaskNotFoundException
from domain.sales.filters import TaskFilters


@pytest.mark.asyncio
async def test_get_task_by_id_success(
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
    task_result, *_ = await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal_id,
            title=task_title,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=faker.text(),
            due_date=date.today() + timedelta(days=1),
        ),
    )
    created_task: TaskEntity = task_result

    retrieved_task = await mediator.handle_query(
        GetTaskByIdQuery(
            task_id=created_task.oid,
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    assert retrieved_task.oid == created_task.oid
    assert retrieved_task.title.as_generic_type() == task_title
    assert retrieved_task.deal_id == deal_id


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(
    mediator: Mediator,
):
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name="Test Org"),
    )
    organization_id = org_result.oid
    user_id = uuid4()
    non_existent_id = uuid4()

    with pytest.raises(TaskNotFoundException) as exc_info:
        await mediator.handle_query(
            GetTaskByIdQuery(
                task_id=non_existent_id,
                organization_id=organization_id,
                user_id=user_id,
                user_role="owner",
            ),
        )

    assert exc_info.value.task_id == non_existent_id


@pytest.mark.asyncio
async def test_get_tasks_query_success(
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

    task1_result, *_ = await mediator.handle_command(
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

    task2_result, *_ = await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal_id,
            title=faker.sentence(),
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=faker.text(),
            due_date=date.today() + timedelta(days=2),
        ),
    )

    filters = TaskFilters(organization_id=organization_id)
    tasks, count = await mediator.handle_query(
        GetTasksQuery(
            filters=filters,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    tasks_list = list(tasks)
    assert count >= 2
    assert len(tasks_list) >= 2

    task_ids = [t.oid for t in tasks_list]
    assert task1_result.oid in task_ids
    assert task2_result.oid in task_ids


@pytest.mark.asyncio
async def test_get_tasks_query_with_deal_id_filter(
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
    deal1_id = deal1_result.oid

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
    deal2_id = deal2_result.oid

    await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal1_id,
            title=faker.sentence(),
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=faker.text(),
            due_date=date.today() + timedelta(days=1),
        ),
    )

    await mediator.handle_command(
        CreateTaskCommand(
            deal_id=deal2_id,
            title=faker.sentence(),
            organization_id=organization_id,
            user_id=owner_user_id,
            user_role="owner",
            description=faker.text(),
            due_date=date.today() + timedelta(days=1),
        ),
    )

    filters = TaskFilters(organization_id=organization_id, deal_id=deal1_id)
    tasks, count = await mediator.handle_query(
        GetTasksQuery(
            filters=filters,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    tasks_list = list(tasks)
    assert count >= 1
    assert all(t.deal_id == deal1_id for t in tasks_list)


@pytest.mark.asyncio
async def test_get_tasks_query_with_pagination(
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

    for _ in range(3):
        await mediator.handle_command(
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

    filters = TaskFilters(organization_id=organization_id, page=1, page_size=2)
    tasks, count = await mediator.handle_query(
        GetTasksQuery(
            filters=filters,
            user_id=owner_user_id,
            user_role="owner",
        ),
    )

    tasks_list = list(tasks)
    assert count >= 3
    assert len(tasks_list) <= 2
