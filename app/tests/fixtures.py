from infrastructure.database.repositories.dummy.organizations.members import DummyInMemoryOrganizationMemberRepository
from infrastructure.database.repositories.dummy.organizations.organizations import DummyInMemoryOrganizationRepository
from infrastructure.database.repositories.dummy.sales.activities import DummyInMemoryActivityRepository
from infrastructure.database.repositories.dummy.sales.contacts import DummyInMemoryContactRepository
from infrastructure.database.repositories.dummy.sales.deals import DummyInMemoryDealRepository
from infrastructure.database.repositories.dummy.sales.tasks import DummyInMemoryTaskRepository
from infrastructure.database.repositories.dummy.users.users import DummyInMemoryUserRepository
from punq import (
    Container,
    Scope,
)

from application.container import _init_container
from domain.organizations.interfaces.repositories.members import BaseOrganizationMemberRepository
from domain.organizations.interfaces.repositories.organizations import BaseOrganizationRepository
from domain.sales.interfaces.repositories.activities import BaseActivityRepository
from domain.sales.interfaces.repositories.contacts import BaseContactRepository
from domain.sales.interfaces.repositories.deals import BaseDealRepository
from domain.sales.interfaces.repositories.tasks import BaseTaskRepository
from domain.users.interfaces.repositories.users import BaseUserRepository


def init_dummy_container() -> Container:
    container = _init_container()

    # Регистрируем репозитории (dummy для начала)
    container.register(
        BaseOrganizationRepository,
        DummyInMemoryOrganizationRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseOrganizationMemberRepository,
        DummyInMemoryOrganizationMemberRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseUserRepository,
        DummyInMemoryUserRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseContactRepository,
        DummyInMemoryContactRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseDealRepository,
        DummyInMemoryDealRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseTaskRepository,
        DummyInMemoryTaskRepository,
        scope=Scope.singleton,
    )
    container.register(
        BaseActivityRepository,
        DummyInMemoryActivityRepository,
        scope=Scope.singleton,
    )

    return container
