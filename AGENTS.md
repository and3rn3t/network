# Project Guidelines (AGENTS.md)

<!--
  Single source of truth for AI assistant instructions in this repo.
  CLAUDE.md is a thin pointer to this file — edit HERE.
  .github/instructions/copilot-instructions.md has longer Python patterns and examples.
-->

## Project Overview

**NetworkMonitor** — monitoring for a local UniFi Network Controller (UDM Pro): a Python
API client and collector that polls devices/clients into SQLite, plus analytics, rule-based
alerting with notifications (email, Slack, Discord, webhooks), reports and exports. Two web
surfaces sit on top: a React dashboard and an API (a FastAPI version for local use and a
Hono version on Cloudflare Workers).

## Layout

The repo has four independent parts, each with its own dependencies:

```
src/                      # core Python package (run from repo root; tests import `src.…`)
  unifi_client.py, unifi_controller.py, client_factory.py   # UniFi API clients
  collector/              # unifi_collector, data_collector, orchestrator, scheduler
  database/               # database.py, models, repositories/, schema*.sql, migrations/
  analytics/              # analytics_engine, forecasting, machine_learning, unifi_analytics
  alerts/                 # alert_engine, alert_manager, notification_manager, notifiers/, cli.py
  reports/, export/       # HTML/PDF reports, CSV/JSON export
collect_unifi_data.py     # main collection entry point
config.example.py         # copy to config.py (gitignored) with controller credentials
tests/                    # pytest (responses-mocked API; alerts/, database/)
examples/                 # runnable usage examples (list_hosts, run_collector, dashboard_rich, …)
scripts/                  # ad-hoc DB/collection/diagnostic scripts and PowerShell helpers
backend/                  # FastAPI web API (src/main.py, src/api/*, JWT auth) — own requirements.txt
frontend/                 # React 19 + Vite + MUI/Ant Design dashboard — npm, own package.json
workers/                  # Hono API on Cloudflare Workers: D1 (network-db), KV (CACHE), Durable Object WebSocket
docs/                     # guides/, reference/, development/, archive/ — index in docs/README.md
```

Keep the repo root minimal: utilities go in `scripts/`, docs in `docs/`.

## Commands

```bash
# Core Python (repo root)
pip install -r requirements.txt          # requests, python-dotenv, rich (+ weasyprint for PDF) and pytest deps
cp config.example.py config.py           # then fill in controller host/credentials (API_TYPE local|cloud)
python scripts/create_fresh_db.py        # create the SQLite database
python collect_unifi_data.py --verbose   # one collection run (--daemon --interval N to keep polling)
python -m pytest tests/                  # tests

# Alert CLI (needs src/ on PYTHONPATH)
PYTHONPATH=src python -m alerts.cli rule list

# FastAPI backend
cd backend && pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --port 8000   # docs at /docs

# Frontend
cd frontend && npm ci
npm run dev        # Vite
npm run lint
npm run build:check  # tsc -b && vite build (`build` skips type checking)

# Workers API
cd workers && npm install
npm run dev          # wrangler dev
npm run type-check
```

There is no CI test workflow yet — run the relevant checks locally.

## Deployment

- **Frontend → Cloudflare Pages** project `network` (`frontend/wrangler.toml`), via
  `deploy-cloudflare.yml` on push to `main` touching `frontend/**`.
- **Workers API → Cloudflare Workers** `network-api` (`workers/wrangler.toml`; D1
  `network-db`, KV `CACHE`, Durable Object `WebSocketDurableObject`), via
  `deploy-workers.yml` on push to `main` touching `workers/**`. Schema: `workers/schema.sql`.
- Pushing to `main` deploys — never commit, push or deploy unless explicitly asked.
- Secrets: `wrangler secret put JWT_SECRET` (the `[vars]` value is a placeholder);
  controller credentials live only in the gitignored `config.py` / `.env` files.

## Conventions

- Python: PEP 8, type hints on all signatures, Google-style docstrings, f-strings, specific
  exception types (see `src/exceptions.py`), `src/retry.py` for retries. Avoid circular
  imports with `TYPE_CHECKING` guards and lazy imports.
- Data access goes through `src/database/repositories/`, not raw SQL in callers.
- Tests mock HTTP with `responses`; never hit a real controller from tests.
- Never log controller credentials, API keys or JWTs.

## Known gotchas

- `frontend/src/api/client.ts` reads `VITE_API_URL`, but `frontend/.env.production` and
  the Pages deploy workflow set `VITE_API_BASE_URL` — check which one a change relies on.
- Many `scripts/test_*.py` and `backend/test_*.py` files are manual scripts, not pytest
  tests; the pytest suite is `tests/`.
