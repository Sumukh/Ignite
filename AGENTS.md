# AGENTS.md

This file is a practical runbook for AI coding agents working in this repository.

## What This Repo Is

Ignite is a Flask starter app with:
- Auth (email/password + Google OAuth)
- Team/membership model
- Billing hooks (Stripe)
- Basic REST API
- Admin/dashboard UI

Primary package: `appname/`

## Fast Start (Local Development)

```bash
cd /Users/sumukh/code/Ignite
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

# Seed local sqlite DB with starter users
APPNAME_ENV=dev ./manage.py resetdb

# Run app
FLASK_APP=manage FLASK_ENV=development flask run
```

Open: `http://localhost:5000`

Seeded dev logins after `resetdb`:
- `user@example.com` / `test`
- `admin@example.com` / `admin`

## Core Commands

```bash
# Lint
make lint

# Full tracked test suite (recommended)
make agent-test

# Full test discovery (also runs untracked local tests, if any)
APPNAME_ENV=test ./manage.py test --coverage

# Or raw pytest
APPNAME_ENV=test pytest --cov-report=term-missing --cov=appname tests/

# Quick DB reset + seed (dev only)
APPNAME_ENV=dev ./manage.py resetdb
```

## Project Map

- `manage.py`: CLI entrypoint (`server`, `resetdb`, `test`, etc.)
- `wsgi.py`: production WSGI app object
- `appname/__init__.py`: app factory, extension setup, blueprint registration
- `appname/settings.py`: `DevConfig`, `TestConfig`, `ProdConfig`
- `appname/controllers/`: web routes
- `appname/controllers/dashboard/`: logged-in dashboard routes
- `appname/controllers/oauth/google.py`: Google OAuth flow
- `appname/controllers/webhooks/stripe.py`: Stripe webhook handler
- `appname/api/`: API blueprints/resources (`/api/v1/...`)
- `appname/models/`: SQLAlchemy models
- `appname/templates/`: Jinja templates
- `tests/`: pytest suite
- `documentation/`: deployment/integration notes

## Config + Environment

Minimum local env:
- `APPNAME_ENV=dev` for local app
- `APPNAME_ENV=test` for tests
- `FLASK_APP=manage`
- `FLASK_ENV=development` for local debug run

Optional integrations (see `.env.local.sample`):
- Google OAuth: `GOOGLE_CONSUMER_KEY`, `GOOGLE_CONSUMER_SECRET`
- Stripe: `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_KEY`
- Storage: `STORAGE_PROVIDER`, `STORAGE_KEY`, `STORAGE_SECRET`

Load example local secrets:

```bash
cp .env.local.sample .env.local
source .env.local
```

## Agent Workflow Expectations

1. Read `README.md` and this file before changing code.
2. Prefer focused edits in existing modules over broad refactors.
3. After code changes:
   - Run targeted tests for touched area.
   - Run `make agent-test` before final handoff when feasible.
4. If models/migrations behavior is touched, run a local DB reset (`APPNAME_ENV=dev ./manage.py resetdb`) and sanity-check login/dashboard flows.
5. Do not commit secrets or `.env.local`.

## Common Change Targets

- Auth/login/signup: `appname/controllers/auth.py`, `appname/forms/login.py`, auth templates
- Dashboard pages: `appname/controllers/dashboard/*.py` + `appname/templates/dashboard/*`
- Team logic: `appname/models/teams/*` and `appname/controllers/dashboard/team.py`
- API behavior: `appname/api/*.py`
- Billing/webhooks: `appname/controllers/webhooks/stripe.py`, `appname/billing_plans.py`, `appname/services/stripe.py`

## Known Gotchas

- Tests rely on `APPNAME_ENV=test`; forgetting it can cause wrong config usage.
- Test fixture data (`tests/conftest.py`) uses different seed passwords than dev `resetdb`.
- `appname/api/` auth expects `api_key` in query string.
- In dev/test, some async behavior is intentionally synchronous (`RQ_ASYNC=False` in settings).

## References

- Main docs: `README.md`
- OAuth notes: `documentation/oauth.md`
- Stripe notes: `documentation/stripe.md`
- Deployment example: `documentation/dokku.md`
