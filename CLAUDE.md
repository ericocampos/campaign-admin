# CLAUDE.md

Notes for Claude Code (or any agent) working on this repo.

## Commands

```sh
uv sync                                    # install deps
uv run pytest -v                           # run tests
uv run ruff check . && uv run ruff format --check .
uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8001 --reload
docker compose up --build                  # container run
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

## Architecture

Single-process FastAPI + SQLAlchemy + Jinja + HTMX. No SPA, no build step. SQLite file lives in `./data/`. See `docs/superpowers/specs/2026-04-22-campaign-admin-design.md` for the full design (note: `docs/superpowers/` is gitignored — available locally only).

## Conventions

- **All POST forms use HTMX.** The CSRF token is sent via `hx-headers` on `<body>` in `base.html`. Don't use plain HTML form POSTs — they bypass the CSRF header.
- **Markdown anywhere in user input** goes through `app.markdown.render_markdown` which sanitises via `bleach` before rendering. Never render user markdown without going through this helper.
- **Bind guard** (`ensure_loopback_bind`) is a user-intent check, bypassed when `IN_DOCKER=1`. In Docker, host-side isolation (`127.0.0.1:8001:8001` in compose) provides the real restriction.
- **Routes return HTML fragments**, not JSON. When a POST completes, return the updated partial so HTMX can swap it.
- **Tests use in-memory SQLite** via `conftest.py` with `StaticPool` so all connections share one DB. CSRF is disabled by default in test fixtures; use the dedicated CSRF test file to cover that path.

## Not in scope

Auth, file uploads, multi-user, production deploy, reminders, drag-drop, charts. Do not add these without a new spec.
