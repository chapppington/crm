from datetime import date

from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from faker import Faker
from httpx import Response

from domain.sales.entities import DealEntity


@pytest.mark.asyncio
async def test_get_tasks_empty(
    app: FastAPI,
    org_client: TestClient,
):
    url = app.url_path_for("get_tasks")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["items"] == []
    assert json_response["data"]["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_create_task_success(
    app: FastAPI,
    org_client: TestClient,
    deal: DealEntity,
    faker: Faker,
):
    url = app.url_path_for("create_task")
    title = faker.sentence()

    response: Response = org_client.post(
        url=url,
        json={
            "deal_id": str(deal.oid),
            "title": title,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["data"]["title"] == title
    assert json_response["data"]["deal_id"] == str(deal.oid)
    assert json_response["data"]["is_done"] is False
    assert "id" in json_response["data"]


@pytest.mark.asyncio
async def test_create_task_with_description_and_due_date(
    app: FastAPI,
    org_client: TestClient,
    deal: DealEntity,
    faker: Faker,
):
    url = app.url_path_for("create_task")
    title = faker.sentence()
    description = faker.text()
    due_date = date.today()

    response: Response = org_client.post(
        url=url,
        json={
            "deal_id": str(deal.oid),
            "title": title,
            "description": description,
            "due_date": due_date.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["data"]["title"] == title
    assert json_response["data"]["description"] == description
    assert json_response["data"]["due_date"] == due_date.isoformat()


@pytest.mark.asyncio
async def test_get_tasks_with_task(
    app: FastAPI,
    org_client: TestClient,
    deal: DealEntity,
    faker: Faker,
):
    create_url = app.url_path_for("create_task")
    title = faker.sentence()

    create_response: Response = org_client.post(
        url=create_url,
        json={
            "deal_id": str(deal.oid),
            "title": title,
        },
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    task_id = create_response.json()["data"]["id"]

    get_url = app.url_path_for("get_tasks")
    response: Response = org_client.get(url=get_url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response["data"]["items"]) == 1
    assert json_response["data"]["items"][0]["id"] == task_id
    assert json_response["data"]["items"][0]["title"] == title


@pytest.mark.asyncio
async def test_get_task_by_id(
    app: FastAPI,
    org_client: TestClient,
    deal: DealEntity,
    faker: Faker,
):
    create_url = app.url_path_for("create_task")
    title = faker.sentence()

    create_response: Response = org_client.post(
        url=create_url,
        json={
            "deal_id": str(deal.oid),
            "title": title,
        },
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    task_id = create_response.json()["data"]["id"]

    get_url = app.url_path_for("get_task", task_id=task_id)
    response: Response = org_client.get(url=get_url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["id"] == task_id
    assert json_response["data"]["title"] == title


@pytest.mark.asyncio
async def test_update_task(
    app: FastAPI,
    org_client: TestClient,
    deal: DealEntity,
    faker: Faker,
):
    create_url = app.url_path_for("create_task")
    title = faker.sentence()

    create_response: Response = org_client.post(
        url=create_url,
        json={
            "deal_id": str(deal.oid),
            "title": title,
        },
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    task_id = create_response.json()["data"]["id"]

    update_url = app.url_path_for("update_task", task_id=task_id)
    new_title = faker.sentence()
    new_description = faker.text()

    update_response: Response = org_client.patch(
        url=update_url,
        json={
            "title": new_title,
            "description": new_description,
            "is_done": True,
        },
    )

    assert update_response.status_code == status.HTTP_200_OK
    json_response = update_response.json()
    assert json_response["data"]["title"] == new_title
    assert json_response["data"]["description"] == new_description
    assert json_response["data"]["is_done"] is True
