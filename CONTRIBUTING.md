# Contributing

Thanks for your interest. A few rules:

## License

By contributing, you agree your contributions are licensed under the PolyForm Noncommercial 1.0.0 license that covers this project. This is a **source-available, non-commercial** license. If that doesn't work for you, don't contribute.

## Workflow

1. Fork and branch off `main`.
2. Run `uv sync`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format .` before pushing.
3. Open a PR. CI must pass.
4. Keep PRs small and focused. One concern per PR.

## Local dev

```bash
uv sync
uv run uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8001
```

## Tests

`uv run pytest`. Add tests for any behaviour you change. Route tests use FastAPI `TestClient` with an in-memory SQLite fixture.

## Style

ruff handles formatting and lint. No exceptions.
