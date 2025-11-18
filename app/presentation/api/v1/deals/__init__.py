from presentation.api.v1.deals.activities import router as activities_router
from presentation.api.v1.deals.handlers import router


router.include_router(activities_router)

__all__ = ("router",)
