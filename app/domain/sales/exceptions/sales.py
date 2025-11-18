from dataclasses import dataclass
from datetime import date
from uuid import UUID

from domain.base.exceptions import DomainException


@dataclass(eq=False)
class SalesException(DomainException):
    @property
    def message(self) -> str:
        return "Sales exception occurred"


# Contact exceptions
@dataclass(eq=False)
class EmptyContactNameException(SalesException):
    @property
    def message(self) -> str:
        return "Contact name is empty"


@dataclass(eq=False)
class EmptyContactEmailException(SalesException):
    @property
    def message(self) -> str:
        return "Contact email is empty"


@dataclass(eq=False)
class EmptyContactPhoneException(SalesException):
    @property
    def message(self) -> str:
        return "Contact phone is empty"


@dataclass(eq=False)
class InvalidContactEmailException(SalesException):
    email: str

    @property
    def message(self) -> str:
        return f"Invalid contact email format: {self.email}"


@dataclass(eq=False)
class InvalidContactPhoneException(SalesException):
    phone: str

    @property
    def message(self) -> str:
        return f"Invalid contact phone format: {self.phone}"


@dataclass(eq=False)
class ContactNotFoundException(SalesException):
    contact_id: UUID

    @property
    def message(self) -> str:
        return f"Contact with id {self.contact_id} not found"


@dataclass(eq=False)
class ContactHasActiveDealsException(SalesException):
    contact_id: UUID

    @property
    def message(self) -> str:
        return f"Cannot delete contact {self.contact_id} because it has active deals"


# Deal exceptions
@dataclass(eq=False)
class EmptyDealTitleException(SalesException):
    @property
    def message(self) -> str:
        return "Deal title is empty"


@dataclass(eq=False)
class EmptyDealStatusException(SalesException):
    @property
    def message(self) -> str:
        return "Deal status is empty"


@dataclass(eq=False)
class EmptyDealStageException(SalesException):
    @property
    def message(self) -> str:
        return "Deal stage is empty"


@dataclass(eq=False)
class EmptyCurrencyException(SalesException):
    @property
    def message(self) -> str:
        return "Currency is empty"


@dataclass(eq=False)
class InvalidDealAmountException(SalesException):
    amount: float

    @property
    def message(self) -> str:
        return f"Invalid deal amount: {self.amount}. Amount must be non-negative"


@dataclass(eq=False)
class InvalidCurrencyException(SalesException):
    currency: str

    @property
    def message(self) -> str:
        return f"Invalid currency: {self.currency}"


@dataclass(eq=False)
class InvalidDealStatusException(SalesException):
    status: str

    @property
    def message(self) -> str:
        return f"Invalid deal status: {self.status}"


@dataclass(eq=False)
class InvalidDealStageException(SalesException):
    stage: str

    @property
    def message(self) -> str:
        return f"Invalid deal stage: {self.stage}"


@dataclass(eq=False)
class DealNotFoundException(SalesException):
    deal_id: UUID

    @property
    def message(self) -> str:
        return f"Deal with id {self.deal_id} not found"


@dataclass(eq=False)
class CannotCloseDealWithZeroAmountException(SalesException):
    deal_id: UUID

    @property
    def message(self) -> str:
        return f"Cannot close deal {self.deal_id} with status 'won' because amount is zero or negative"


@dataclass(eq=False)
class DealStageRollbackNotAllowedException(SalesException):
    deal_id: UUID
    current_stage: str
    new_stage: str

    @property
    def message(self) -> str:
        return (
            f"Cannot rollback deal {self.deal_id} stage from {self.current_stage} to {self.new_stage}. "
            f"Only admin and owner can rollback stages"
        )


@dataclass(eq=False)
class ContactOrganizationMismatchException(SalesException):
    contact_id: UUID
    contact_organization_id: UUID
    deal_organization_id: UUID

    @property
    def message(self) -> str:
        return (
            f"Contact {self.contact_id} belongs to organization {self.contact_organization_id}, "
            f"but deal belongs to organization {self.deal_organization_id}. "
            f"Contact and deal must belong to the same organization"
        )


@dataclass(eq=False)
class AccessDeniedException(SalesException):
    resource_type: str
    resource_id: UUID
    user_id: UUID

    @property
    def message(self) -> str:
        return f"User {self.user_id} does not have access to {self.resource_type} {self.resource_id}"


@dataclass(eq=False)
class ResourceNotFoundInOrganizationException(SalesException):
    resource_type: str
    resource_id: UUID
    organization_id: UUID

    @property
    def message(self) -> str:
        return f"{self.resource_type} {self.resource_id} not found in organization {self.organization_id}"


# Task exceptions
@dataclass(eq=False)
class EmptyTaskTitleException(SalesException):
    @property
    def message(self) -> str:
        return "Task title is empty"


@dataclass(eq=False)
class EmptyTaskDescriptionException(SalesException):
    @property
    def message(self) -> str:
        return "Task description is empty"


@dataclass(eq=False)
class InvalidTaskDueDateException(SalesException):
    due_date: date
    today: date

    @property
    def message(self) -> str:
        return f"Task due date {self.due_date} cannot be in the past. Today is {self.today}"


@dataclass(eq=False)
class TaskNotFoundException(SalesException):
    task_id: UUID

    @property
    def message(self) -> str:
        return f"Task with id {self.task_id} not found"


@dataclass(eq=False)
class CannotCreateTaskForOtherUserDealException(SalesException):
    deal_id: UUID
    user_id: UUID

    @property
    def message(self) -> str:
        return (
            f"Member role cannot create task for deal {self.deal_id} "
            f"that belongs to another user. Deal owner is {self.user_id}"
        )


# Activity exceptions
@dataclass(eq=False)
class EmptyActivityTypeException(SalesException):
    @property
    def message(self) -> str:
        return "Activity type is empty"


@dataclass(eq=False)
class InvalidActivityTypeException(SalesException):
    activity_type: str

    @property
    def message(self) -> str:
        return f"Invalid activity type: {self.activity_type}"


@dataclass(eq=False)
class ActivityNotFoundException(SalesException):
    activity_id: UUID

    @property
    def message(self) -> str:
        return f"Activity with id {self.activity_id} not found"
