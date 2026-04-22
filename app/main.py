import os

from fastapi import FastAPI

from app.config import Settings
from app.db import init_db
from app.routes import health
from app.security import SecurityHeadersMiddleware, ensure_loopback_bind


def create_app() -> FastAPI:
    settings = Settings()
    if not os.getenv("IN_DOCKER"):
        ensure_loopback_bind(settings.app_host)

    import app.db as db_module
    if db_module._engine is None:
        init_db(settings.database_url)

    app = FastAPI(title="Campaign Admin", version="0.1.0")
    app.add_middleware(SecurityHeadersMiddleware)
    app.include_router(health.router)
    return app
