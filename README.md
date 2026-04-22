# Campaign Admin

A local-first web tool for managing marketing and launch campaigns -- structured tracking (phases, posts, metrics, logs) plus per-campaign markdown notes, all in one SQLite database.

## Status

Source-available under PolyForm Noncommercial 1.0.0. Free for personal, educational, and non-profit use. Not for commercial use.

## Security

This tool has **no authentication** and is designed to run locally only. It binds to `127.0.0.1:8001` and refuses to start if it detects it is listening on a public network interface. Do not expose it to the internet.

## Quick start

```bash
git clone https://github.com/ericocampos/campaign-admin
cd campaign-admin
cp .env.example .env
docker compose up
# open http://127.0.0.1:8001
```

## Development

See CONTRIBUTING.md.

## License

PolyForm Noncommercial 1.0.0 -- see LICENSE.
