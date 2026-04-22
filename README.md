# Campaign Admin

A local-first, Docker-packaged web tool for running and tracking marketing/launch campaigns. Structured tracking (phases, steps, metrics, logs) plus per-campaign markdown notes, all in one SQLite database.

**Source-available** under PolyForm Noncommercial 1.0.0, free for personal, educational, and non-profit use. **Not for commercial use.** See LICENSE.

## Features

- Multiple campaigns with status (draft/active/paused/done/archived).
- Per-campaign markdown overview, renderable and editable.
- Ordered **steps** (posts/milestones) with flexible JSON metrics, scheduled/posted timestamps, URL, content + retro markdown.
- Grouped **checklists** with toggleable status.
- Generic **log** table with categories (feature requests, bugs, signals, kill-switches, or anything you invent), with a repeat-increment button for running tallies.
- Four-tab campaign dashboard with HTMX partial swaps (no full page reloads).

## Security

This tool has **no authentication** and is designed to run **locally only**. It binds to `127.0.0.1:8001` via Docker Compose. Do not expose it to the public internet.

Additional protections:
- CSRF (double-submit cookie, `starlette-csrf`).
- Security headers: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
- Markdown sanitisation via `bleach` (allowlist of safe tags).
- Loopback bind guard at app startup (bypassed inside Docker where host-level port publishing enforces the restriction).

See SECURITY.md for the full threat model and how to report a vulnerability.

## Quick start

```bash
git clone https://github.com/ericocampos/campaign-admin
cd campaign-admin
cp .env.example .env
# edit SECRET_KEY to a random 32+ byte string:
#   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
docker compose up -d
open http://127.0.0.1:8001
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check .
uv run uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8001 --reload
```

See CONTRIBUTING.md.

## Stack

Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Jinja2, HTMX, Pico.css, SQLite, Docker.

## Licensing

PolyForm Noncommercial 1.0.0. Technically **source-available**, not OSI "open source" -- the non-commercial restriction is a field-of-use clause that OSI does not recognise. Honesty matters, so the project does not claim to be open source. Personal, hobby, educational, and non-profit use is explicitly allowed.
