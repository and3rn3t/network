# CLAUDE.md — NetworkMonitor (network)

**Read `AGENTS.md` first** — it maps the four parts (core Python `src/`, `backend/`,
`frontend/`, `workers/`), their commands and deploy flow. This file only adds
Claude-specific notes.

UniFi controller monitoring: Python collector/analytics/alerts + React dashboard + Hono API
on Cloudflare Workers.

## Claude-specific notes

- Work out which part a change touches and run that part's checks: `python -m pytest tests/`
  (core), `npm run lint && npm run build:check` (frontend), `npm run type-check` (workers).
  No CI runs tests, so run them yourself.
- Pushes to `main` under `frontend/**` or `workers/**` deploy automatically — don't commit
  or push unless asked.
- Never read or print `config.py` or `.env` values; they hold controller credentials.
- When a Cloudflare MCP connector is available, use it to inspect D1/KV/Workers instead of
  guessing from `wrangler.toml`.
