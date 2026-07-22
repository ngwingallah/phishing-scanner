# Deployment Guide — PhishGuard

The project brief caps undeployed web applications at 50% of the score, so
this step is worth doing properly. Target: a public URL where the scanner
page and the Swagger docs both load.

Everything below is free and needs no card.

---

## Before you start

Make sure the repository is on GitHub and up to date:

```bash
git add .
git commit -m "Ready to deploy"
git push
```

Confirm these files are in the repo root: `requirements.txt`,
`render.yaml`, and the `app/` package.

---

## Deploy on Render (about 10 minutes)

1. Go to **render.com** and sign up with your GitHub account.
2. Click **New** → **Web Service**.
3. Connect your GitHub account and pick the `phishing-scanner` repository.
4. Render reads `render.yaml`, so the fields should fill themselves. Confirm:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance type:** Free
5. Click **Create Web Service** and wait for the build log to finish. First
   build takes roughly 3–5 minutes.
6. When the status turns **Live**, open the URL Render gives you
   (something like `https://phishguard-xxxx.onrender.com`).

Check all three of these work on the live URL:

- `/` — the scanner page loads and shows "14 rules"
- `/docs` — Swagger UI lists all six endpoints
- Click a sample button — a verdict appears and the history table fills

---

## Important: the free tier sleeps

A free Render service spins down after about 15 minutes of inactivity. The
next request wakes it, which takes **30–60 seconds**.

For your presentation, **open the live URL about two minutes before you
start** so the service is awake when you demo. Do not discover this in front
of the examiner.

---

## Storage behaviour

With no `DATABASE_URL` set, the app writes to a local SQLite file. Render's
free filesystem is ephemeral, so history resets when the service restarts.
That is acceptable for a demo — you will be creating fresh scans live
anyway.

If you want history to persist:

1. In Render, create a **PostgreSQL** instance (free tier).
2. Copy its **Internal Database URL**.
3. In your web service, go to **Environment** → add
   `DATABASE_URL` = that connection string.
4. In `requirements.txt`, uncomment the `psycopg2-binary` line, then commit
   and push.

No application code changes — `database.py` already reads `DATABASE_URL` and
converts the `postgres://` prefix that Render supplies into the
`postgresql://` form SQLAlchemy expects. That is a good design point to
mention in the viva: the storage backend is configuration, not code.

---

## Troubleshooting

**Build fails on `psycopg2-binary`.** You have uncommented it without
supplying a Postgres database. Comment it out again, or finish the Postgres
setup above.

**Service builds but shows "Application failed to respond".** Check the
start command binds correctly — it must include `--host 0.0.0.0 --port
$PORT`. Binding to `127.0.0.1` will not accept external traffic.

**Page loads but scans fail.** Open the browser console. If requests to
`/scan` return 500, check the Render logs tab for the traceback.

**Fonts do not load.** The page pulls Archivo and JetBrains Mono from Google
Fonts. If the exam room has no internet, the layout still works — it falls
back to system fonts. Worth knowing before you present.

---

## Fallback: demo locally

If deployment fails on the day, you can still demo from your laptop:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000`. Keep this as a backup even if the deploy
succeeds — a local server does not depend on the venue's wifi.

---

## Evidence to capture for the report

Take these screenshots once the deployment is live, for Chapter Four
(Results and Discussions):

1. The Render dashboard showing the service **Live**, with the URL visible.
2. The scanner page on the live URL, with a Dangerous verdict displayed.
3. The Swagger UI on the live URL listing all endpoints.
4. A `POST /scan` request and its JSON response, executed in Swagger.
5. The history table with several scans.
6. Your terminal showing `24 passed`.
