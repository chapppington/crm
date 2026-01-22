from fastapi import FastAPI

from presentation.admin import setup_admin
from presentation.api.exceptions import setup_exception_handlers
from presentation.api.healthcheck import healthcheck_router
from presentation.api.v1 import v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CRM",
        description="CRM",
        docs_url="/api/docs",
        debug=True,
    )

    setup_exception_handlers(app)

    app.include_router(healthcheck_router)
    app.include_router(v1_router, prefix="/api/v1")

    setup_admin(app)

    return app
