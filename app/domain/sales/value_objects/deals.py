from dataclasses import dataclass
from enum import Enum

from domain.base.value_object import BaseValueObject
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


class DealStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


class DealStage(str, Enum):
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"


@dataclass(frozen=True)
class DealTitleValueObject(BaseValueObject):
    value: str
    MAX_LENGTH = 255

    def validate(self):
        if not self.value:
            raise EmptyDealTitleException()

        if len(self.value) > self.MAX_LENGTH:
            raise EmptyDealTitleException()

    def as_generic_type(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class DealAmountValueObject(BaseValueObject):
    value: float

    def validate(self):
        if self.value < 0:
            raise InvalidDealAmountException(amount=self.value)

    def as_generic_type(self) -> float:
        return float(self.value)


@dataclass(frozen=True)
class CurrencyValueObject(BaseValueObject):
    value: str
    SUPPORTED_CURRENCIES = {"USD", "EUR", "RUB", "GBP", "JPY", "CNY"}

    def validate(self):
        if not self.value:
            raise EmptyCurrencyException()

        if self.value.upper() not in self.SUPPORTED_CURRENCIES:
            raise InvalidCurrencyException(currency=self.value)

    def as_generic_type(self) -> str:
        return str(self.value).upper()


@dataclass(frozen=True)
class DealStatusValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyDealStatusException()

        try:
            DealStatus(self.value)
        except ValueError:
            raise InvalidDealStatusException(status=str(self.value))

    def as_generic_type(self) -> DealStatus:
        return DealStatus(self.value)


@dataclass(frozen=True)
class DealStageValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyDealStageException()

        try:
            DealStage(self.value)
        except ValueError:
            raise InvalidDealStageException(stage=str(self.value))

    def as_generic_type(self) -> DealStage:
        return DealStage(self.value)
