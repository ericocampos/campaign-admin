import os
import re

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.db import init_db
from app.routes import health
from app.routes import markdown as md_routes
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
    if settings.csrf_enabled:
        from starlette_csrf import CSRFMiddleware
        app.add_middleware(
            CSRFMiddleware,
            secret=settings.secret_key,
            cookie_name="csrftoken",
            header_name="x-csrftoken",
            cookie_secure=False,
            cookie_samesite="strict",
            exempt_urls=[re.compile(r"^/health$"), re.compile(r"^/static/.*")],
        )
    app.state.templates = Jinja2Templates(directory="app/templates")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(health.router)
    app.include_router(md_routes.router)
    return app
