from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response


@pytest.mark.asyncio
async def test_get_contacts_empty(
    app: FastAPI,
    org_client: TestClient,
):
    url = app.url_path_for("get_contacts")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["items"] == []
    assert json_response["data"]["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_create_contact_success(
    app: FastAPI,
    org_client: TestClient,
    faker: Faker,
):
    url = app.url_path_for("create_contact")
    name = faker.name()

    response: Response = org_client.post(
        url=url,
        json={"name": name},
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["data"]["name"] == name
    assert "id" in json_response["data"]


@pytest.mark.asyncio
async def test_create_contact_with_email(
    app: FastAPI,
    org_client: TestClient,
    faker: Faker,
):
    url = app.url_path_for("create_contact")
    name = faker.name()
    email = faker.email()

    response: Response = org_client.post(
        url=url,
        json={"name": name, "email": email},
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["data"]["name"] == name
    assert json_response["data"]["email"] == email


@pytest.mark.asyncio
async def test_get_contacts_with_contact(
    app: FastAPI,
    org_client: TestClient,
    faker: Faker,
):
    create_url = app.url_path_for("create_contact")
    name = faker.name()

    create_response: Response = org_client.post(
        url=create_url,
        json={"name": name},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    contact_id = create_response.json()["data"]["id"]

    get_url = app.url_path_for("get_contacts")
    response: Response = org_client.get(url=get_url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response["data"]["items"]) == 1
    assert json_response["data"]["items"][0]["id"] == contact_id
    assert json_response["data"]["items"][0]["name"] == name
