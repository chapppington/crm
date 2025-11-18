from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response

from application.mediator import Mediator
from application.organizations.commands import (
    AddMemberCommand,
    CreateOrganizationCommand,
)
from application.sales.commands import (
    CreateContactCommand,
    CreateDealCommand,
)
from domain.sales.entities import ContactEntity


@pytest.mark.asyncio
async def test_get_deals_empty(
    app: FastAPI,
    org_client: TestClient,
):
    url = app.url_path_for("get_deals")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["items"] == []
    assert json_response["data"]["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_create_deal_success(
    app: FastAPI,
    org_client: TestClient,
    contact: ContactEntity,
    faker: Faker,
):
    url = app.url_path_for("create_deal")
    title = faker.sentence()

    response: Response = org_client.post(
        url=url,
        json={
            "contact_id": str(contact.oid),
            "title": title,
            "amount": 1000.0,
            "currency": "USD",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["data"]["title"] == title
    assert json_response["data"]["amount"] == 1000.0
    assert json_response["data"]["currency"] == "USD"
    assert json_response["data"]["contact_id"] == str(contact.oid)
    assert "id" in json_response["data"]


@pytest.mark.asyncio
async def test_get_deals_with_deal(
    app: FastAPI,
    org_client: TestClient,
    contact: ContactEntity,
    faker: Faker,
):
    create_url = app.url_path_for("create_deal")
    title = faker.sentence()

    create_response: Response = org_client.post(
        url=create_url,
        json={
            "contact_id": str(contact.oid),
            "title": title,
            "amount": 5000.0,
            "currency": "EUR",
        },
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    deal_id = create_response.json()["data"]["id"]

    get_url = app.url_path_for("get_deals")
    response: Response = org_client.get(url=get_url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response["data"]["items"]) == 1
    assert json_response["data"]["items"][0]["id"] == deal_id
    assert json_response["data"]["items"][0]["title"] == title
    assert json_response["data"]["items"][0]["amount"] == 5000.0


@pytest.mark.asyncio
async def test_get_deal_by_id(
    app: FastAPI,
    org_client: TestClient,
    contact: ContactEntity,
    faker: Faker,
):
    create_url = app.url_path_for("create_deal")
    title = faker.sentence()

    create_response: Response = org_client.post(
        url=create_url,
        json={
            "contact_id": str(contact.oid),
            "title": title,
            "amount": 2000.0,
            "currency": "RUB",
        },
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    deal_id = create_response.json()["data"]["id"]

    get_url = app.url_path_for("get_deal", deal_id=deal_id)
    response: Response = org_client.get(url=get_url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["id"] == deal_id
    assert json_response["data"]["title"] == title
    assert json_response["data"]["amount"] == 2000.0
    assert json_response["data"]["currency"] == "RUB"


@pytest.mark.asyncio
async def test_get_deal_by_id_from_another_organization_returns_404(
    app: FastAPI,
    org_client: TestClient,
    mediator: Mediator,
    authenticated_user,
    faker: Faker,
):
    other_org_result, *_ = await mediator.handle_command(
        CreateOrganizationCommand(name=faker.company()),
    )
    other_organization_id = other_org_result.oid

    other_user_id = authenticated_user.oid
    await mediator.handle_command(
        AddMemberCommand(
            organization_id=other_organization_id,
            user_id=other_user_id,
            role="owner",
        ),
    )

    contact_result, *_ = await mediator.handle_command(
        CreateContactCommand(
            organization_id=other_organization_id,
            owner_user_id=other_user_id,
            name=faker.name(),
        ),
    )

    deal_result, *_ = await mediator.handle_command(
        CreateDealCommand(
            organization_id=other_organization_id,
            contact_id=contact_result.oid,
            owner_user_id=other_user_id,
            title=faker.sentence(),
            amount=1000.0,
            currency="USD",
        ),
    )
    other_deal_id = deal_result.oid

    get_url = app.url_path_for("get_deal", deal_id=other_deal_id)
    response: Response = org_client.get(url=get_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
