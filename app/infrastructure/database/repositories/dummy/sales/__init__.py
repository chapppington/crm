from infrastructure.database.repositories.dummy.sales.activities import DummyInMemoryActivityRepository
from infrastructure.database.repositories.dummy.sales.contacts import DummyInMemoryContactRepository
from infrastructure.database.repositories.dummy.sales.deals import DummyInMemoryDealRepository
from infrastructure.database.repositories.dummy.sales.tasks import DummyInMemoryTaskRepository


__all__ = [
    "DummyInMemoryActivityRepository",
    "DummyInMemoryContactRepository",
    "DummyInMemoryDealRepository",
    "DummyInMemoryTaskRepository",
]
