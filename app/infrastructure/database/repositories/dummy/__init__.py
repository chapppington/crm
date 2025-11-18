from infrastructure.database.repositories.dummy.activity import DummyInMemoryActivityRepository
from infrastructure.database.repositories.dummy.contact import DummyInMemoryContactRepository
from infrastructure.database.repositories.dummy.deal import DummyInMemoryDealRepository
from infrastructure.database.repositories.dummy.member import DummyInMemoryOrganizationMemberRepository
from infrastructure.database.repositories.dummy.organization import DummyInMemoryOrganizationRepository
from infrastructure.database.repositories.dummy.task import DummyInMemoryTaskRepository
from infrastructure.database.repositories.dummy.user import DummyInMemoryUserRepository


__all__ = [
    "DummyInMemoryActivityRepository",
    "DummyInMemoryContactRepository",
    "DummyInMemoryDealRepository",
    "DummyInMemoryOrganizationMemberRepository",
    "DummyInMemoryOrganizationRepository",
    "DummyInMemoryTaskRepository",
    "DummyInMemoryUserRepository",
]
