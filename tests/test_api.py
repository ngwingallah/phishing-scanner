"""Endpoint tests that exercise the full request/response cycle."""


def test_health(client):
    assert client.get("/health").status_code == 200


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
