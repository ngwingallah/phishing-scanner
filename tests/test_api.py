"""Endpoint tests that exercise the full request/response cycle."""


def test_health(client):
    assert client.get("/health").status_code == 200


def test_checks_endpoint_lists_the_rule_set(client):
    r = client.get("/checks")
    assert r.status_code == 200
    rules = r.json()
    assert len(rules) == 14
    assert all("name" in rule and "weight" in rule for rule in rules)


def test_root_serves_the_frontend(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "PhishGuard" in r.text


def test_flags_include_points(client):
    r = client.post("/scan", json={"url": "http://192.168.0.1/login.exe"})
    flags = r.json()["flags"]
    assert flags, "expected this URL to trigger at least one rule"
    assert all(isinstance(f["points"], int) and f["points"] > 0 for f in flags)


def test_scan_returns_a_verdict(client):
    r = client.post("/scan", json={"url": "http://paypal.secure-login.xyz@1.2.3.4/verify"})
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] in {"Safe", "Suspicious", "Dangerous"}
    assert isinstance(body["flags"], list)


def test_scan_persists_and_is_listed(client):
    client.post("/scan", json={"url": "https://example.com"})
    r = client.get("/scans")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_scan_by_id(client):
    created = client.post("/scan", json={"url": "https://example.com"}).json()
    r = client.get(f"/scans/{created['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_missing_scan_returns_404(client):
    assert client.get("/scans/999999").status_code == 404


def test_missing_url_field_is_rejected(client):
    # Pydantic should reject a body without the required 'url'.
    assert client.post("/scan", json={}).status_code == 422


# --- session isolation ---------------------------------------------------

def test_history_is_scoped_to_the_session(client):
    a = {"X-Session-Id": "session-aaa"}
    b = {"X-Session-Id": "session-bbb"}

    client.post("/scan", json={"url": "https://alpha-only.example.com"}, headers=a)
    client.post("/scan", json={"url": "https://beta-only.example.com"}, headers=b)

    a_urls = [row["url"] for row in client.get("/scans", headers=a).json()]
    b_urls = [row["url"] for row in client.get("/scans", headers=b).json()]

    assert "https://alpha-only.example.com" in a_urls
    assert "https://beta-only.example.com" not in a_urls
    assert "https://beta-only.example.com" in b_urls
    assert "https://alpha-only.example.com" not in b_urls


def test_cannot_read_another_sessions_scan(client):
    owner = {"X-Session-Id": "owner-session"}
    other = {"X-Session-Id": "other-session"}

    created = client.post(
        "/scan", json={"url": "https://private.example.com"}, headers=owner
    ).json()

    assert client.get(f"/scans/{created['id']}", headers=owner).status_code == 200
    assert client.get(f"/scans/{created['id']}", headers=other).status_code == 404


def test_new_session_starts_with_empty_history(client):
    fresh = {"X-Session-Id": "brand-new-session"}
    assert client.get("/scans", headers=fresh).json() == []
