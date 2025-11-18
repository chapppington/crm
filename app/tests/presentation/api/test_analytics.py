from fastapi import (
    FastAPI,
    status,
)
from fastapi.testclient import TestClient

import pytest
from httpx import Response


@pytest.mark.asyncio
async def test_get_deal_summary_empty(
    app: FastAPI,
    org_client: TestClient,
):
    url = app.url_path_for("get_deal_summary")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["total_count"] == 0
    assert json_response["data"]["new_count"] == 0
    assert json_response["data"]["in_progress_count"] == 0
    assert json_response["data"]["won_count"] == 0
    assert json_response["data"]["lost_count"] == 0
    assert json_response["data"]["total_won_amount"] == 0.0


@pytest.mark.asyncio
async def test_get_deal_summary_with_deal(
    app: FastAPI,
    org_client: TestClient,
    deal,  # фикстура создает deal в БД для проверки статистики
):
    url = app.url_path_for("get_deal_summary")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["total_count"] == 1
    assert json_response["data"]["new_count"] == 1
    assert json_response["data"]["in_progress_count"] == 0
    assert json_response["data"]["won_count"] == 0
    assert json_response["data"]["lost_count"] == 0


@pytest.mark.asyncio
async def test_get_deal_funnel_empty(
    app: FastAPI,
    org_client: TestClient,
):
    url = app.url_path_for("get_deal_funnel")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["qualification_count"] == 0
    assert json_response["data"]["proposal_count"] == 0
    assert json_response["data"]["negotiation_count"] == 0
    assert json_response["data"]["closed_count"] == 0


@pytest.mark.asyncio
async def test_get_deal_funnel_with_deal(
    app: FastAPI,
    org_client: TestClient,
    deal,  # фикстура создает deal в БД
):
    url = app.url_path_for("get_deal_funnel")

    response: Response = org_client.get(url=url)

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["data"]["qualification_count"] == 1
    assert json_response["data"]["proposal_count"] == 0
    assert json_response["data"]["negotiation_count"] == 0
    assert json_response["data"]["closed_count"] == 0
