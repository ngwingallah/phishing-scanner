# Test Case Document — PhishGuard

**Course:** SEN2241 — Object Oriented Analysis, Design and Implementation
**System under test:** PhishGuard heuristic phishing-URL scanner
**Test date:** 22 July 2026
**Automated result:** 27 / 27 passing (`pytest -q`)

Two kinds of test are recorded here:

- **Automated (TC-A…)** — executed by the pytest suite in `tests/`. The
  "Test function" column names the exact test, so any result can be
  reproduced with `pytest -k <name>`.
- **Manual (TC-M…)** — user-interface behaviour verified by hand in the
  browser, since it involves rendering and interaction.

---

## 1. Unit tests — heuristic checks

Each check is tested in isolation with a crafted URL. These need no
database or server.

| ID | Test objective | Input | Expected result | Test function | Status |
|----|----------------|-------|-----------------|---------------|--------|
| TC-A01 | Raw IP host is detected | `http://192.168.0.1/login` | Check triggers | `test_ip_address_triggers_on_raw_ip` | Pass |
| TC-A02 | Normal domain is not flagged as an IP | `https://google.com` | Check does not trigger | `test_ip_address_passes_on_domain` | Pass |
| TC-A03 | `@` obfuscation is detected | `http://safe@evil.com` | Check triggers | `test_at_symbol_triggers` | Pass |
| TC-A04 | Abused TLD is detected, normal TLD is not | `http://foo.xyz` / `http://foo.com` | Triggers / does not trigger | `test_risky_tld` | Pass |
| TC-A05 | Punycode homoglyph host is detected | `http://xn--pple-43d.com` | Check triggers | `test_punycode_triggers` | Pass |
| TC-A06 | Known URL shortener is detected | `http://bit.ly/abc` | Check triggers | `test_shortener_triggers` | Pass |
| TC-A07 | Missing HTTPS is detected | `http://example.com` / `https://example.com` | Triggers / does not trigger | `test_no_https` | Pass |
| TC-A08 | Brand name on a foreign domain is detected | `http://paypal.secure-login.xyz` | Check triggers | `test_brand_impersonation_triggers_on_fake_domain` | Pass |
| TC-A09 | Brand name on its real domain is not flagged | `https://www.paypal.com/signin` | Check does not trigger | `test_brand_impersonation_passes_on_real_domain` | Pass |
| TC-A10 | Dangerous file extension is detected | `http://x.com/setup.exe` | Check triggers | `test_file_extension_triggers` | Pass |
| TC-A11 | Non-standard port is detected, standard is not | `http://x.com:4444/` / `https://x.com/` | Triggers / does not trigger | `test_non_standard_port` | Pass |

## 2. Unit tests — risk analyzer

Verifies aggregation, thresholds and the score cap.

| ID | Test objective | Input | Expected result | Test function | Status |
|----|----------------|-------|-----------------|---------------|--------|
| TC-A12 | A clean URL is classified Safe | `https://www.google.com` | verdict = `Safe` | `test_clean_url_is_safe` | Pass |
| TC-A13 | An obvious phishing URL is Dangerous | paypal lure with raw IP and `@` | verdict = `Dangerous`, score > 45 | `test_obvious_phish_is_dangerous` | Pass |
| TC-A14 | Score never exceeds the maximum | URL triggering many rules at once | score ≤ 100 | `test_score_is_capped_at_100` | Pass |
| TC-A15 | Only triggered checks are reported as flags | `https://www.google.com` | every reported outcome has `triggered = True` | `test_only_triggered_flags_are_reported` | Pass |

## 3. Integration tests — API endpoints

Executed through FastAPI's `TestClient` against a throwaway SQLite
database, so the full request → analyze → persist → respond cycle runs.

| ID | Test objective | Request | Expected result | Test function | Status |
|----|----------------|---------|-----------------|---------------|--------|
| TC-A16 | Service health endpoint responds | `GET /health` | 200 OK | `test_health` | Pass |
| TC-A17 | Rule catalogue is exposed | `GET /checks` | 200 OK, 14 rules, each with name and weight | `test_checks_endpoint_lists_the_rule_set` | Pass |
| TC-A18 | Frontend page is served at root | `GET /` | 200 OK, HTML contains "PhishGuard" | `test_root_serves_the_frontend` | Pass |
| TC-A19 | Scan returns a valid verdict and flags | `POST /scan` with a phishing URL | 200 OK, verdict ∈ {Safe, Suspicious, Dangerous} | `test_scan_returns_a_verdict` | Pass |
| TC-A20 | Each flag carries its point value | `POST /scan` with `http://192.168.0.1/login.exe` | every flag has integer `points` > 0 | `test_flags_include_points` | Pass |
| TC-A21 | A scan is persisted and appears in history | `POST /scan` then `GET /scans` | 200 OK, at least one record returned | `test_scan_persists_and_is_listed` | Pass |
| TC-A22 | A single scan is retrievable by id | `POST /scan` then `GET /scans/{id}` | 200 OK, returned id matches | `test_get_scan_by_id` | Pass |
| TC-A23 | Unknown scan id is rejected | `GET /scans/999999` | 404 Not Found | `test_missing_scan_returns_404` | Pass |
| TC-A24 | Malformed request body is rejected | `POST /scan` with `{}` | 422 Unprocessable Entity | `test_missing_url_field_is_rejected` | Pass |

## 3b. Integration tests — session isolation

Verifies that one visitor cannot see another visitor's scan history.

| ID | Test objective | Request | Expected result | Test function | Status |
|----|----------------|---------|-----------------|---------------|--------|
| TC-A25 | History is scoped to the calling session | Two scans under different `X-Session-Id` values, then `GET /scans` as each | Each session sees only its own URL | `test_history_is_scoped_to_the_session` | Pass |
| TC-A26 | One session cannot read another's scan | `GET /scans/{id}` with a different `X-Session-Id` | 404 Not Found (owner still gets 200) | `test_cannot_read_another_sessions_scan` | Pass |
| TC-A27 | A new session starts empty | `GET /scans` with an unused `X-Session-Id` | 200 OK, empty list | `test_new_session_starts_with_empty_history` | Pass |

## 4. Manual test cases — user interface

Performed in a browser against a running server (`uvicorn app.main:app`).

| ID | Test objective | Steps | Expected result | Status |
|----|----------------|-------|-----------------|--------|
| TC-M01 | Page loads and reports the rule count | Open `/` | Masthead shows "14 rules"; history section renders | Pass |
| TC-M02 | Safe sample produces a Safe verdict | Click **a safe link** | Verdict `Safe` in green, score 0, "No risk signals triggered" | Pass |
| TC-M03 | Phishing sample produces a Dangerous verdict | Click **a phishing link** | Verdict `Dangerous` in red, score 59, 4 signals listed | Pass |
| TC-M04 | Mobile-money lure is detected | Click **a mobile-money lure** | Verdict `Dangerous`, score 60, 5 signals including brand impersonation and `.apk` | Pass |
| TC-M05 | URL dissection is displayed | Scan any URL | Scheme, host and path are shown underlined and labelled | Pass |
| TC-M06 | Score ledger reflects the weights | Scan the phishing sample | Ledger shows one segment per triggered rule, widths proportional to points | Pass |
| TC-M07 | Signals are ordered by severity | Scan the phishing sample | Highest-point signal appears first | Pass |
| TC-M08 | History updates after a scan | Scan a URL, observe the table | New row appears at the top with URL, score, verdict and timestamp | Pass |
| TC-M09 | Empty input is rejected client-side | Click **Scan** with the field empty | Message "Enter a URL to scan."; no network request sent | Pass |
| TC-M10 | Server outage is handled gracefully | Stop the server, click **Scan** | Message "Could not reach the scanner. Is the server running?" | Pass |
| TC-M11 | Enter key submits the form | Type a URL, press Enter | Scan runs, same as clicking Scan | Pass |
| TC-M12 | Keyboard navigation is visible | Tab through the page | Focus outline visible on input, buttons and links | Pass |
| TC-M13 | Layout is responsive | Narrow the window to phone width | Content reflows, no horizontal scrolling of the page | Pass |
| TC-M14 | Swagger documentation is reachable | Open `/docs` | All six endpoints listed and executable | Pass |
| TC-M15 | History is private to the browser | Scan a URL, then open the same site in a private/incognito window | The incognito window shows an empty history; the original still shows its scans | Pass |
| TC-M16 | Session survives a reload | Scan a URL, refresh the page | History still lists the scan | Pass |
| TC-M17 | Migration preserves an existing database | Start the server over a `scanner.db` created before sessions existed | Server starts, `session_id` column is added, old rows are retained | Pass |

---

## 5. Summary

| Category | Cases | Passed | Failed |
|----------|------:|-------:|-------:|
| Unit — checks | 11 | 11 | 0 |
| Unit — analyzer | 4 | 4 | 0 |
| Integration — API | 9 | 9 | 0 |
| Integration — session isolation | 3 | 3 | 0 |
| Manual — UI | 17 | 17 | 0 |
| **Total** | **44** | **44** | **0** |

**How to reproduce the automated results**

```bash
pip install -r requirements-dev.txt
pytest -q          # expected: 27 passed
```

**Known limitations (not defects)**

- Heuristic detection can be evaded by a URL that avoids all 14 signals,
  and can produce false positives — a legitimate sub-brand such as
  `googleusercontent.com` will trigger the brand-impersonation rule.
- Scores are relative risk indicators, not probabilities.
- The scanner inspects the URL string only; it does not fetch the page,
  so it cannot judge page content or certificate validity.
- Scan history is tied to a browser, not a person. Clearing browser storage
  or switching devices starts a fresh, empty history. This is a deliberate
  trade-off: it avoids collecting any personal data, at the cost of history
  not following the user across devices.
