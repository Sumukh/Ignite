# Agent Quickstart

Use this when you want to get productive in this repo with minimal context.

## 1) Setup

```bash
cd /Users/sumukh/code/Ignite
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) Initialize Local Data

```bash
APPNAME_ENV=dev ./manage.py resetdb
```

This seeds:
- `user@example.com` / `test`
- `admin@example.com` / `admin`

## 3) Run App

```bash
FLASK_APP=manage flask --debug run
```

Open [http://localhost:5000](http://localhost:5000)

## 4) Validate Changes

```bash
# Fast smoke tests
make agent-smoke

# Full tracked tests + coverage (recommended)
make agent-test

# Optional: full test discovery (also includes untracked local tests)
APPNAME_ENV=test ./manage.py test --coverage
```

## 5) High-Signal File Locations

- App factory and blueprint wiring: `appname/__init__.py`
- Environment configs: `appname/settings.py`
- Auth + signup/login: `appname/controllers/auth.py`
- Dashboard routes: `appname/controllers/dashboard/`
- API resources: `appname/api/`
- Core models: `appname/models/`
- Templates: `appname/templates/`
- Tests: `tests/`

## Troubleshooting

- `flask run` cannot find app:
  - Ensure `FLASK_APP=manage`
- Tests fail with config mismatch:
  - Ensure `APPNAME_ENV=test`
- OAuth/Stripe paths not working locally:
  - Load local env vars from `.env.local` (see `.env.local.sample`)
