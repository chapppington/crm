from fastapi import APIRouter

from presentation.api.v1.analytics import analytics_router
from presentation.api.v1.contacts import router as contacts_router
from presentation.api.v1.deals import router as deals_router
from presentation.api.v1.organizations import router as organizations_router
from presentation.api.v1.tasks import router as tasks_router
from presentation.api.v1.user.handlers import router as user_router


v1_router = APIRouter()

v1_router.include_router(user_router)
v1_router.include_router(organizations_router)
v1_router.include_router(contacts_router)
v1_router.include_router(deals_router)
v1_router.include_router(tasks_router)
v1_router.include_router(analytics_router)
