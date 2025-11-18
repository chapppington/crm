import pytest

from domain.sales.exceptions.sales import (
    EmptyCurrencyException,
    EmptyDealStageException,
    EmptyDealStatusException,
    EmptyDealTitleException,
    InvalidCurrencyException,
    InvalidDealAmountException,
    InvalidDealStageException,
    InvalidDealStatusException,
)
from domain.sales.value_objects.deal import (
    CurrencyValueObject,
    DealAmountValueObject,
    DealStage,
    DealStageValueObject,
    DealStatus,
    DealStatusValueObject,
    DealTitleValueObject,
)


@pytest.mark.parametrize(
    "title_value,expected",
    [
        ("Website Redesign", "Website Redesign"),
        ("A" * 255, "A" * 255),
        ("Deal #123", "Deal #123"),
    ],
)
def test_deal_title_valid(title_value, expected):
    title = DealTitleValueObject(title_value)
    assert title.as_generic_type() == expected
    assert len(title.as_generic_type()) == len(expected)


@pytest.mark.parametrize(
    "title_value",
    [
        "",
        "A" * 256,
    ],
)
def test_deal_title_invalid(title_value):
    with pytest.raises(EmptyDealTitleException):
        DealTitleValueObject(title_value)


@pytest.mark.parametrize(
    "amount_value,expected",
    [
        (10000.0, 10000.0),
        (0.0, 0.0),
        (1.5, 1.5),
        (999999.99, 999999.99),
    ],
)
def test_deal_amount_valid(amount_value, expected):
    amount = DealAmountValueObject(amount_value)
    assert amount.as_generic_type() == expected


@pytest.mark.parametrize(
    "amount_value",
    [
        -100.0,
        -0.01,
        -999999.99,
    ],
)
def test_deal_amount_negative(amount_value):
    with pytest.raises(InvalidDealAmountException):
        DealAmountValueObject(amount_value)


@pytest.mark.parametrize(
    "currency_value,expected",
    [
        ("USD", "USD"),
        ("eur", "EUR"),
        ("RUB", "RUB"),
        ("GBP", "GBP"),
        ("JPY", "JPY"),
        ("CNY", "CNY"),
    ],
)
def test_currency_valid(currency_value, expected):
    currency = CurrencyValueObject(currency_value)
    assert currency.as_generic_type() == expected


@pytest.mark.parametrize(
    "currency_value,exception",
    [
        ("", EmptyCurrencyException),
        ("XYZ", InvalidCurrencyException),
        ("BTC", InvalidCurrencyException),
    ],
)
def test_currency_invalid(currency_value, exception):
    with pytest.raises(exception):
        CurrencyValueObject(currency_value)


@pytest.mark.parametrize(
    "status_value,expected_status",
    [
        ("new", DealStatus.NEW),
        ("in_progress", DealStatus.IN_PROGRESS),
        ("won", DealStatus.WON),
        ("lost", DealStatus.LOST),
    ],
)
def test_deal_status_valid(status_value, expected_status):
    status = DealStatusValueObject(status_value)
    assert status.as_generic_type() == expected_status


@pytest.mark.parametrize(
    "status_value,exception",
    [
        ("", EmptyDealStatusException),
        ("invalid_status", InvalidDealStatusException),
        ("closed", InvalidDealStatusException),
    ],
)
def test_deal_status_invalid(status_value, exception):
    with pytest.raises(exception):
        DealStatusValueObject(status_value)


@pytest.mark.parametrize(
    "stage_value,expected_stage",
    [
        ("qualification", DealStage.QUALIFICATION),
        ("proposal", DealStage.PROPOSAL),
        ("negotiation", DealStage.NEGOTIATION),
        ("closed", DealStage.CLOSED),
    ],
)
def test_deal_stage_valid(stage_value, expected_stage):
    stage = DealStageValueObject(stage_value)
    assert stage.as_generic_type() == expected_stage


@pytest.mark.parametrize(
    "stage_value,exception",
    [
        ("", EmptyDealStageException),
        ("invalid_stage", InvalidDealStageException),
        ("new", InvalidDealStageException),
    ],
)
def test_deal_stage_invalid(stage_value, exception):
    with pytest.raises(exception):
        DealStageValueObject(stage_value)
