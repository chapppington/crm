from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response

from domain.organizations.entities import OrganizationEntity


@pytest.mark.asyncio
async def test_create_organization_success(
    app: FastAPI,
    authenticated_client: TestClient,
    faker: Faker,
):
    url = app.url_path_for("create_organization")
    name = faker.company()

    response: Response = authenticated_client.post(
        url=url,
        json={"name": name},
    )

    assert response.status_code == status.HTTP_201_CREATED

    json_response = response.json()
    assert json_response["data"]["name"] == name
    assert "id" in json_response["data"]


@pytest.mark.asyncio
async def test_create_organization_empty_name(
    app: FastAPI,
    authenticated_client: TestClient,
):
    url = app.url_path_for("create_organization")

    response: Response = authenticated_client.post(
        url=url,
        json={"name": ""},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "errors" in response.json()


@pytest.mark.asyncio
async def test_get_user_organizations_empty(
    app: FastAPI,
    authenticated_client: TestClient,
):
    url = app.url_path_for("get_user_organizations")

    response: Response = authenticated_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["organizations"] == []


@pytest.mark.asyncio
async def test_get_user_organizations_with_organizations(
    app: FastAPI,
    authenticated_client: TestClient,
    organization_with_member: OrganizationEntity,
):
    url = app.url_path_for("get_user_organizations")

    response: Response = authenticated_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK

    json_response = response.json()
    org_data = json_response["data"]["organizations"][0]
    assert org_data["organization_id"] == str(organization_with_member.oid)
    assert org_data["role"] == "owner"
