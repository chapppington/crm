from fastapi import FastAPI
from fastapi.testclient import TestClient

import pytest
import pytest_asyncio
from faker import Faker
from presentation.api.auth import auth_service
from presentation.api.main import create_app
from punq import Container

from application.container import init_container
from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    CreateOrganizationCommand,
)
from application.sales.commands import (
    CreateContactCommand,
    CreateDealCommand,
)
from application.users.commands import CreateUserCommand
from domain.organizations.entities import OrganizationEntity
from domain.sales.entities import (
    ContactEntity,
    DealEntity,
)
from domain.users.entities import UserEntity
from tests.fixtures import init_dummy_container


@pytest.fixture
def container() -> Container:
    return init_dummy_container()


@pytest.fixture
def app(container: Container) -> FastAPI:
    app = create_app()
    app.dependency_overrides[init_container] = lambda: container

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app=app)


@pytest.fixture
def mediator(container: Container) -> Mediator:
    return container.resolve(Mediator)


@pytest_asyncio.fixture
async def authenticated_user(mediator: Mediator, faker: Faker) -> UserEntity:
    email = faker.email()
    password = faker.password(length=12)
    name = faker.name()

    result, *_ = await mediator.handle_command(
        CreateUserCommand(email=email, password=password, name=name),
    )

    return result


@pytest_asyncio.fixture
async def authenticated_client(
    client: TestClient,
    authenticated_user: UserEntity,
) -> TestClient:
    user_id = str(authenticated_user.oid)
    access_token = auth_service.create_access_token(uid=user_id)
    refresh_token = auth_service.create_refresh_token(uid=user_id)

    client.cookies.set("access_token", access_token)
    client.cookies.set("refresh_token", refresh_token)

    return client


@pytest_asyncio.fixture
async def organization_with_member(
    mediator: Mediator,
    authenticated_user: UserEntity,
    faker: Faker,
) -> OrganizationEntity:
    org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    organization = org_result

    await mediator.handle_command(
        AddMemberCommand(
            organization_id=organization.oid,
            user_id=authenticated_user.oid,
            role="owner",
        ),
    )

    return organization


@pytest_asyncio.fixture
async def org_client(
    authenticated_client: TestClient,
    organization_with_member: OrganizationEntity,
) -> TestClient:
    authenticated_client.headers.update(
        {"X-Organization-Id": str(organization_with_member.oid)},
    )
    return authenticated_client


@pytest_asyncio.fixture
async def contact(
    mediator: Mediator,
    organization_with_member: OrganizationEntity,
    authenticated_user: UserEntity,
    faker: Faker,
) -> ContactEntity:
    result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=organization_with_member.oid,
            owner_user_id=authenticated_user.oid,
            name=faker.name(),
            email=faker.email(),
        ),
    )
    return result


@pytest_asyncio.fixture
async def deal(
    mediator: Mediator,
    organization_with_member: OrganizationEntity,
    authenticated_user: UserEntity,
    contact: ContactEntity,
    faker: Faker,
) -> DealEntity:
    result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=organization_with_member.oid,
            contact_id=contact.oid,
            owner_user_id=authenticated_user.oid,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    return result
