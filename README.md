# PhishGuard — Heuristic Phishing URL Scanner

A small web service that scores a URL for phishing risk using a set of
explainable heuristic rules, then stores every scan. Built for the OOADI
final (SEN2241).

## What it does

Submit a URL and PhishGuard runs it through independent checks (raw IP,
`@` trick, risky TLD, punycode look-alikes, suspicious keywords, and
more). Each check adds weighted risk points; the total maps to a verdict:
**Safe**, **Suspicious**, or **Dangerous**. Every scan is saved and
retrievable through the API.

## Why it demonstrates OOP

- **Abstraction / inheritance:** every heuristic subclasses an abstract
  `Check` (`app/checks/base.py`).
- **Polymorphism:** `RiskAnalyzer` runs each check through the same
  `evaluate()` interface without knowing its internals.
- **Composition:** `RiskAnalyzer` *has a* list of `Check` objects.
- **Strategy pattern:** checks are interchangeable strategies; new rules
  drop in without changing the analyzer (open/closed principle).
- **Repository pattern:** `ScanRepository` isolates all persistence.

## Project structure

```
app/
  main.py         FastAPI app + routes (thin controllers)
  analyzer.py     RiskAnalyzer + ScanReport (scoring logic)
  url.py          ParsedUrl value object
  checks/
    base.py       abstract Check + CheckOutcome
    rules.py      concrete heuristic checks
  models.py       Scan ORM model
  repository.py   ScanRepository (data access)
  schemas.py      Pydantic request/response models
  database.py     engine + session
  static/
    index.html    the web frontend (no build step)
docs/
  product_backlog.md
  sprint_backlog.md
  CODE_WALKTHROUGH.md
tests/            pytest suite (24 tests)
```

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- The app: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API

| Method | Path           | Purpose                         |
|--------|----------------|---------------------------------|
| GET    | `/`            | The scanner web page            |
| POST   | `/scan`        | Analyze a URL, save the result  |
| GET    | `/scans`       | List recent scans               |
| GET    | `/scans/{id}`  | Fetch one scan                  |
| GET    | `/checks`      | List all heuristic rules        |
| GET    | `/health`      | Health check                    |

Example:

```bash
curl -X POST http://127.0.0.1:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-verify.secure-update.xyz@192.168.0.10/login"}'
```

## Deploy on Render

1. Push this repo to GitHub.
2. New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. (Optional) add a Render PostgreSQL instance and set `DATABASE_URL`;
   the app falls back to SQLite if it isn't set.
