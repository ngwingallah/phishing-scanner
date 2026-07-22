# PhishGuard — Code Walkthrough & Defense Prep

Everything built today, what each piece does, where it lives, and the
questions you're likely to be asked. Read top to bottom once; keep the
"Likely questions" section open during the presentation.

---

## 1. What the app does (say this in one breath)

PhishGuard takes a URL, runs it through a set of independent heuristic
checks, adds up risk points from the checks that trigger, and turns the
total into a verdict — **Safe**, **Suspicious**, or **Dangerous**. Every
scan is saved to a database and can be retrieved later. The API documents
itself with Swagger.

It is **not** a machine-learning model. It's a transparent, rule-based
scorer — which is a strength: every verdict comes with reasons.

---

## 2. The layers (this is the architecture answer)

The code is split into three layers plus a contract. This separation is
the whole point of the design — each layer has one job.

```
   HTTP request
        │
┌───────▼─────────────────────────────┐
│ PRESENTATION  →  app/main.py         │  routes only; no logic
├──────────────────────────────────────┤
│ CONTRACT      →  app/schemas.py      │  request/response shapes
├──────────────────────────────────────┤
│ DOMAIN / LOGIC → app/analyzer.py     │  scoring
│                  app/checks/*        │  the rules
│                  app/url.py          │  URL parsing
├──────────────────────────────────────┤
│ DATA          →  app/repository.py   │  DB access
│                  app/models.py       │  the table
│                  app/database.py     │  connection
└──────────────────────────────────────┘
```

If asked "what architecture is this?" → a **layered architecture** with a
**service/domain layer** (the analyzer + checks) separated from the
**data-access layer** (repository) and the **presentation layer** (the
FastAPI routes).

---

## 3. A scan, traced end to end (the most important thing to know)

When someone calls `POST /scan` with `{"url": "..."}`:

1. **`app/main.py` → `scan_url()`** receives the request. FastAPI has
   already validated the body against **`ScanRequest`** (`schemas.py`).
2. It calls **`analyzer.analyze(payload.url)`**.
3. **`RiskAnalyzer.analyze()`** (`analyzer.py`) first calls
   **`ParsedUrl.parse(url)`** (`url.py`) to break the URL into scheme,
   host, path, etc.
4. It loops over its list of checks and calls **`check.evaluate(url)`** on
   each one. Each returns a **`CheckOutcome`** (triggered? how many
   points? why?).
5. It sums the points, caps the total at 100, and calls **`_verdict()`**
   to map the score to Safe / Suspicious / Dangerous. It packages all of
   this into a **`ScanReport`**.
6. Back in the route, **`ScanRepository(db).save(report)`**
   (`repository.py`) writes a **`Scan`** row (`models.py`) to the database.
7. FastAPI serializes that row through **`ScanOut`** (`schemas.py`) and
   returns JSON.

`GET /scans` and `GET /scans/{id}` skip the analyzer — they just ask the
repository to read rows.

Memorize this seven-step chain. If you can walk an examiner through it,
you've shown you understand the whole system.

---

## 4. File-by-file

### `app/url.py` — `ParsedUrl`
A **value object** that wraps Python's `urlparse`. It exposes `scheme`,
`host`, `path`, plus helpers: `labels` (host split on dots), `tld` (last
label), and `length`. Parsing lives here once, so every check works from
the same clean data instead of re-parsing strings.

### `app/checks/base.py` — `Check` and `CheckOutcome`
- **`CheckOutcome`** is a small dataclass: `name`, `triggered` (bool),
  `points` (int), `reason` (str).
- **`Check`** is an **abstract base class** (inherits `ABC`). It defines
  `name`, `weight`, an abstract method `evaluate(url)` that subclasses
  **must** implement, and a helper `_outcome()` that builds a CheckOutcome
  so subclasses don't repeat themselves.

This file is where the examiner will look for **abstraction**.

### `app/checks/rules.py` — the 14 concrete checks
Each is a subclass of `Check` that overrides `evaluate()`. Weights (risk
points added when the check triggers):

| Check | Weight | Fires when… |
|-------|-------:|-------------|
| `IpAddressCheck` | 25 | host is a raw IP, not a domain |
| `BrandImpersonationCheck` | 20 | a known brand (paypal, google…) appears but the real domain doesn't |
| `AtSymbolCheck` | 18 | `@` in the URL (hides real host) |
| `PunycodeCheck` | 15 | host has `xn--` (look-alike/homoglyph) |
| `SubdomainCheck` | 12 | ≥3 subdomain levels |
| `RiskyTldCheck` | 12 | TLD in the abused list (.zip, .xyz, .top…) |
| `SuspiciousFileExtensionCheck` | 12 | link points to `.exe`, `.apk`, `.zip`… |
| `UrlLengthCheck` | 10 | URL longer than 75 chars |
| `DeceptiveHttpsCheck` | 10 | `https` buried inside the host name |
| `SuspiciousKeywordCheck` | 10 | words like login, verify, bank |
| `NonStandardPortCheck` | 10 | explicit non-web port (e.g. `:4444`) |
| `HyphenCheck` | 8 | ≥3 hyphens in the domain |
| `ShortenerCheck` | 8 | known shortener (bit.ly, t.co…) |
| `NoHttpsCheck` | 6 | not served over HTTPS |

`default_checks()` at the bottom returns them as a list — that's what the
analyzer uses by default.

**Tuning note (a deliberate design decision worth mentioning):** a bare
shortener or missing HTTPS scores low on purpose — neither is phishing on
its own, so they only push a URL over the line in combination with other
signals. This keeps false positives down. `BrandImpersonationCheck` is a
broad heuristic: it will also flag legitimate sub-brands (e.g.
`googleusercontent.com`), which is an honest limitation to acknowledge.

### `app/analyzer.py` — `RiskAnalyzer` and `ScanReport`
- **`RiskAnalyzer`** holds a list of `Check` objects (default:
  `default_checks()`). `analyze()` runs them all, sums points, caps at
  `max_score` (100), and assigns a verdict via `_verdict()`.
- Thresholds: score **≤ 20 = Safe**, **21–45 = Suspicious**,
  **> 45 = Dangerous**.
- **`ScanReport`** is the result object: `url`, `score`, `verdict`, all
  `outcomes`, and a `triggered` property (only the checks that fired).

### `app/models.py` — `Scan`
The SQLAlchemy ORM model = the `scans` database table. Columns: `id`,
`url`, `score`, `verdict`, `flags` (JSON list of triggered checks),
`created_at`.

### `app/repository.py` — `ScanRepository`
The **Repository pattern**: all database queries live here. `save(report)`
turns a ScanReport into a Scan row and commits it; `list()` returns recent
scans; `get(id)` fetches one. The routes never touch the database directly.

### `app/database.py`
Creates the SQLAlchemy `engine` and `SessionLocal`. Reads `DATABASE_URL`
from the environment; defaults to a local **SQLite** file. If a Postgres
URL is supplied (e.g. on Render) it uses that instead. `get_db()` is the
dependency that hands a session to each request and closes it after.

### `app/schemas.py` — Pydantic models
The **API contract**, separate from the DB model on purpose.
- `ScanRequest` — the input (`url`), with a phishy example.
- `FlagOut` — one flag (`name`, `reason`).
- `ScanOut` — the response shape (`from_attributes=True` lets it read
  straight from a `Scan` ORM object).

### `app/main.py` — the FastAPI app
Creates the app, enables CORS (so the frontend can call it), builds the
tables on startup, and defines four routes: `GET /health`, `POST /scan`,
`GET /scans`, `GET /scans/{id}`. Routes are **thin** — they delegate to
the analyzer and repository.

### `tests/` — automated tests (pytest)
- `test_checks.py` — unit tests for each heuristic and the analyzer's
  verdicts (no database needed).
- `test_api.py` — endpoint tests through FastAPI's `TestClient`, including
  the 404 and validation (422) paths.
- `conftest.py` — points the app at a throwaway SQLite file so tests never
  touch your dev database.

Run them with: `pip install -r requirements-dev.txt` then `pytest -q`.
Current status: **21 tests passing**.

### Supporting files
- `requirements.txt` — dependencies (FastAPI, Uvicorn, SQLAlchemy,
  Pydantic; psycopg2 only for Postgres deploy).
- `requirements-dev.txt` — adds pytest + httpx for running tests.
- `README.md` — setup, run, deploy.
- `docs/product_backlog.md`, `docs/sprint_backlog.md` — Scrum artifacts.

---

## 5. OOP concepts → exactly where they live

Have a concrete file/class ready for each — examiners ask "show me where."

- **Abstraction** — `Check` (ABC) in `checks/base.py`: defines *what* a
  check must do (`evaluate`), not how.
- **Inheritance** — every class in `rules.py` extends `Check`.
- **Polymorphism** — `RiskAnalyzer.analyze()` calls `check.evaluate(url)`
  on every check through the same interface; each behaves differently.
- **Encapsulation** — internal state is hidden behind a leading
  underscore (`_checks`, `_max_score`, `_db`, `_verdict`, `_outcome`);
  callers use public methods.
- **Composition ("has-a")** — `RiskAnalyzer` *has a* list of `Check`
  objects; `ScanReport` *has* a list of `CheckOutcome`.
- **Strategy pattern** — each check is an interchangeable strategy; the
  analyzer runs them without knowing their internals.
- **Repository pattern** — `ScanRepository` isolates persistence.
- **Single Responsibility Principle** — each class does one thing (a check
  scores one signal; the repository only persists; routes only route).
- **Open/Closed Principle** — add a new heuristic by writing a new
  `Check` subclass; you never modify `RiskAnalyzer`.
- **Dependency Injection** — `get_db` is injected into routes via
  FastAPI's `Depends`.

---

## 6. The scoring algorithm (your "proposed algorithm" slide)

```
score = 0
for each check:
    outcome = check.evaluate(url)
    if outcome.triggered:
        score += check.weight
score = min(score, 100)          # cap

if   score <= 20:  verdict = "Safe"
elif score <= 45:  verdict = "Suspicious"
else:              verdict = "Dangerous"
```

It's a **weighted additive model**. Weights reflect how strongly each
signal indicates phishing (a raw IP = 25 is a big red flag; missing HTTPS
= 6 is minor). This is transparent and explainable, unlike a black-box
classifier — a good design trade-off to state out loud.

---

## 7. Likely defense questions (with answers)

**Q: Why is this object-oriented and not just a script?**
Because behaviour is modelled as objects: an abstract `Check` type with
many subclasses, an analyzer that composes them, a repository for data.
Adding a rule needs no change to existing code.

**Q: Show me polymorphism in your code.**
`RiskAnalyzer.analyze()` loops over checks and calls `evaluate(url)` on
each. Same call, different behaviour per subclass — that's polymorphism.

**Q: What design patterns did you use?**
Strategy (interchangeable checks), Repository (data access), and a Value
Object (`ParsedUrl`).

**Q: How would you add a new phishing rule?**
Write a new subclass of `Check` in `rules.py`, set its `weight`,
implement `evaluate()`, add it to `default_checks()`. Nothing else changes
(open/closed principle).

**Q: Why separate `ScanOut` (schema) from `Scan` (model)?**
The model is how data is stored; the schema is the public API contract.
Keeping them apart means the database can change without breaking the API,
and you never leak internal fields.

**Q: Where's your business logic vs your data logic?**
Business logic is in `analyzer.py` and `checks/`. Data logic is in
`repository.py` and `models.py`. Routes in `main.py` just connect them.

**Q: How do you avoid re-parsing the URL in every check?**
The route parses once into a `ParsedUrl` value object; every check reads
from it.

**Q: What database are you using?**
SQLite locally (zero-config), Postgres in production via `DATABASE_URL`.
SQLAlchemy ORM means the code doesn't change between them.

**Q: How is the API documented?**
FastAPI auto-generates an OpenAPI spec; Swagger UI at `/docs` and ReDoc at
`/redoc` render it — no manual doc writing.

**Q: What are the limitations / future work?**
Heuristics can be evaded and can false-positive (e.g. a legit shortener).
Future work: a machine-learning classifier, a live blocklist feed, and
per-signal weight tuning from real data.

**Q: How would you test it?**
It's already tested — 21 pytest tests in `tests/`. Each `Check.evaluate()`
is unit-tested with crafted URLs, the analyzer's verdicts are checked, and
the endpoints are tested with FastAPI's `TestClient`, including the 404 and
validation (422) cases. Run `pytest -q`.

---

## 8. If you get stuck on one sentence, say this

> "It's a layered, object-oriented phishing scanner. Each detection rule
> is its own class inheriting from an abstract `Check`; a `RiskAnalyzer`
> composes them and adds up weighted risk points into a verdict; a
> `ScanRepository` saves each scan; and FastAPI exposes it as a
> self-documenting REST API."

That single sentence covers abstraction, inheritance, composition, the
patterns, and the architecture.
