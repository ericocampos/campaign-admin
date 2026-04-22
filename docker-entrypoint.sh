#!/usr/bin/env bash
set -euo pipefail

mkdir -p /app/data
uv run alembic upgrade head
exec "$@"
