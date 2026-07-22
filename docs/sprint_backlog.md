# Sprint Backlog — Sprint 1 (solo, one-week resit)

**Sprint length:** Sun 19 Jul – Fri 24 Jul 2026
**Team:** Berlinda Esoh (solo — acting as Product Owner, Scrum Master, and Developer)
**Sprint goal:** ship a deployed phishing-URL scanner with a documented API,
a working frontend, and the full report + presentation.

Status: `To Do` / `In Progress` / `Done`.

| ID   | Task | Story | Day | Status |
|------|------|-------|-----|--------|
| T-1  | Init repo, project structure, `.gitignore` | PB-4 | Sun | Done |
| T-2  | `ParsedUrl` value object | PB-1 | Sun | Done |
| T-3  | Abstract `Check` + `CheckOutcome` | PB-4 | Sun | Done |
| T-4  | Concrete heuristic checks (14 rules) | PB-3 | Sun/Mon | Done |
| T-4b | Automated test suite (21 pytest tests) | PB-11 | Mon | Done |
| T-5  | `RiskAnalyzer` scoring + verdict | PB-2 | Sun | Done |
| T-6  | `Scan` model + `database.py` | PB-5 | Sun | Done |
| T-7  | `ScanRepository` | PB-5 | Sun | Done |
| T-8  | `POST /scan`, `GET /scans`, `GET /scans/{id}` | PB-1, PB-6 | Sun/Mon | Done |
| T-9  | Verify Swagger docs at `/docs` | PB-7 | Mon | Done |
| T-10 | Frontend: scan form + result view | PB-8 | Tue | Done |
| T-11 | Frontend: history table | PB-9 | Tue | Done |
| T-11b| `GET /checks` rule-catalogue endpoint | PB-7 | Tue | Done |
| T-11c| Per-session private history + schema migration | PB-14 | Wed | Done |
| T-12 | UML: use case, class, object, 5 sequence diagrams | — | Wed | Done |
| T-13 | Deploy to Render (config + guide ready; deploy to run) | PB-10 | Wed | In Progress |
| T-14 | Test-case document (38 cases) | PB-11 | Wed | Done |
| T-15 | Project report | — | Thu | To Do |
| T-16 | PowerPoint (≤20 slides) | — | Thu | To Do |
| T-17 | Rehearse + submit | — | Fri | To Do |