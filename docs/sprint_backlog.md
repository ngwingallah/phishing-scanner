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
| T-4  | Concrete heuristic checks (11 rules) | PB-3 | Sun/Mon | In Progress |
| T-5  | `RiskAnalyzer` scoring + verdict | PB-2 | Sun | Done |
| T-6  | `Scan` model + `database.py` | PB-5 | Sun | Done |
| T-7  | `ScanRepository` | PB-5 | Sun | Done |
| T-8  | `POST /scan`, `GET /scans`, `GET /scans/{id}` | PB-1, PB-6 | Sun/Mon | Done |
| T-9  | Verify Swagger docs at `/docs` | PB-7 | Mon | Done |
| T-10 | Frontend: scan form + result view | PB-8 | Tue | To Do |
| T-11 | Frontend: history table | PB-9 | Tue | To Do |
| T-12 | UML: use case, class, object, 5 sequence diagrams | — | Wed | To Do |
| T-13 | Deploy to Render | PB-10 | Wed | To Do |
| T-14 | Test-case document | PB-11 | Wed | To Do |
| T-15 | Project report | — | Thu | To Do |
| T-16 | PowerPoint (≤20 slides) | — | Thu | To Do |
| T-17 | Rehearse + submit | — | Fri | To Do |

**Note on solo scrum:** because this is a sanctioned solo resit, the
five-member team structure is replaced by one person rotating roles. Scrum
discipline is still applied: a groomed product backlog, this sprint
backlog, daily task movement, and a review/retro captured in the report.
