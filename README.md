# DSA Compass

A lightweight, single-user Flask application for tracking a Java DSA curriculum,
daily focus, completion progress, study consistency, and manual revisions.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.
or
`https://dsa-compass.onrender.com/`

The SQLite database is created automatically on first launch and the complete
curriculum is seeded once.

## Deploy

The application is ready for a Python web host such as Render.

- Python runtime: `3.12` (declared in `.python-version`)
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Required environment variable: `SECRET_KEY`
- Recommended environment variable: `DATABASE_URL` from a managed PostgreSQL
  database so progress persists across deployments

Local development continues to use SQLite when `DATABASE_URL` is not set.

## Tests

```powershell
python -m unittest discover -s tests
```
