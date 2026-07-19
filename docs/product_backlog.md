# Product Backlog — PhishGuard

**Product goal:** let a user paste any URL and get an explainable
phishing-risk score, backed by a documented API and a stored scan history.

Priority uses MoSCoW (Must / Should / Could / Won't). Estimates are story
points (relative effort).

| ID   | Epic        | User story | Priority | Est. |
|------|-------------|------------|----------|------|
| PB-1 | Scanning    | As a user, I want to submit a URL so that I can find out if it looks like phishing. | Must | 5 |
| PB-2 | Scanning    | As a user, I want a clear verdict (Safe / Suspicious / Dangerous) so that I can act quickly. | Must | 2 |
| PB-3 | Scanning    | As a user, I want to see *why* a URL was flagged so that I trust the result. | Must | 3 |
| PB-4 | Scanning    | As a maintainer, I want each heuristic to be its own class so that I can add rules without breaking others. | Must | 3 |
| PB-5 | History     | As a user, I want my past scans stored so that I can review them later. | Must | 3 |
| PB-6 | History     | As a user, I want to fetch a single past scan by id so that I can share or revisit it. | Should | 2 |
| PB-7 | API / Docs  | As a developer, I want auto-generated Swagger docs so that the API is easy to consume. | Must | 2 |
| PB-8 | Frontend    | As a user, I want a simple web page to scan a URL so that I don't need the API directly. | Must | 5 |
| PB-9 | Frontend    | As a user, I want to see my scan history in the page so that I can browse results visually. | Should | 3 |
| PB-10| Deployment  | As a user, I want the app available online so that I can use it from anywhere. | Must | 3 |
| PB-11| Quality     | As a maintainer, I want a test-case document so that behaviour is verified. | Should | 2 |
| PB-12| Scanning    | As a maintainer, I want the risk weights tunable so that scoring can be refined. | Could | 2 |
| PB-13| Scanning    | As a user, I could get an ML-based score later so that detection improves beyond heuristics. | Won't (this release) | 8 |

**Definition of Done:** code committed to GitHub, endpoint works in
Swagger, result persisted, and (where relevant) visible in the frontend.
