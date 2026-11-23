"""Hosted-page access control, native file windows and site export of the web interface."""

import os

import pytest

pytest.importorskip("flask")

from arcjetCV.webapp import native_dialog, server  # noqa: E402

SITE = "https://example.org"
TOKEN = "t" * 32


@pytest.fixture
def client():
    saved = dict(server.ACCESS)
    server.ACCESS.update(token=TOKEN, origins={SITE}, loopback=True)
    yield server.app.test_client()
    server.ACCESS.clear()
    server.ACCESS.update(saved)


def test_same_origin_page_needs_no_token(client):
    assert client.get("/api/info").status_code == 200
    r = client.get("/api/info", headers={"Sec-Fetch-Site": "same-origin"})
    assert r.status_code == 200


def test_unknown_website_is_refused(client):
    r = client.get("/api/info", headers={"Origin": "https://evil.example", "Sec-Fetch-Site": "cross-site"})
    assert r.status_code == 403
    assert "Access-Control-Allow-Origin" not in r.headers


def test_simple_cross_site_post_cannot_write_files(client, tmp_path):
    target = tmp_path / "x.json"
    r = client.post(
        "/api/calibration/save",
        data='{"path": "%s", "calibration": {"pixels_per_mm": 1}}' % target,
        headers={"Origin": "https://evil.example", "Content-Type": "text/plain", "Sec-Fetch-Site": "cross-site"},
    )
    assert r.status_code == 403
    assert not target.exists()


def test_allowed_site_needs_the_token(client):
    h = {"Origin": SITE, "Sec-Fetch-Site": "cross-site"}
    assert client.get("/api/info", headers=h).status_code == 401
    r = client.get("/api/info", headers={**h, "X-ArcjetCV-Token": TOKEN})
    assert r.status_code == 200
    assert r.headers["Access-Control-Allow-Origin"] == SITE
    assert client.get("/api/info?token=" + TOKEN, headers=h).status_code == 200
    assert client.get("/api/info", headers={**h, "X-ArcjetCV-Token": "wrong" * 8}).status_code == 401


def test_preflight_allows_token_header(client):
    r = client.options(
        "/api/info",
        headers={"Origin": SITE, "Access-Control-Request-Method": "POST",
                 "Access-Control-Request-Private-Network": "true"},
    )
    assert r.status_code == 204
    assert "X-ArcjetCV-Token" in r.headers["Access-Control-Allow-Headers"]
    assert r.headers["Access-Control-Allow-Private-Network"] == "true"


def test_ping_reports_status_to_any_site(client):
    r = client.get("/api/ping", headers={"Origin": "https://other.example", "Sec-Fetch-Site": "cross-site"})
    assert r.status_code == 200
    assert r.json["origin_allowed"] is False and r.json["token_ok"] is False
    r = client.get("/api/ping", headers={"Origin": SITE, "Sec-Fetch-Site": "cross-site", "X-ArcjetCV-Token": TOKEN})
    assert r.json["origin_allowed"] is True and r.json["token_ok"] is True


def test_dns_rebinding_host_is_refused(client):
    assert client.get("/api/info", headers={"Host": "evil.example:5050"}).status_code == 403


def test_native_dialog_returns_paths(client, monkeypatch):
    seen = {}

    def fake_ask(**kw):
        seen.update(kw)
        return ["/data/run1.mp4"]

    monkeypatch.setattr(native_dialog, "ask", fake_ask)
    r = client.post("/api/dialog", json={"mode": "open", "kind": "video", "title": "Open video"})
    assert r.status_code == 200
    assert r.json == {"cancelled": False, "paths": ["/data/run1.mp4"]}
    assert ".mp4" in seen["exts"] and seen["mode"] == "open"

    monkeypatch.setattr(native_dialog, "ask", lambda **kw: [])
    assert client.post("/api/dialog", json={"mode": "save"}).json["cancelled"] is True


def test_native_dialog_unavailable_falls_back(client, monkeypatch):
    def unavailable(**kw):
        raise native_dialog.DialogUnavailable("no display")

    monkeypatch.setattr(native_dialog, "ask", unavailable)
    assert client.post("/api/dialog", json={"kind": "json"}).status_code == 501


def test_export_site(tmp_path):
    dest = server.export_site(str(tmp_path / "site"))
    html = open(os.path.join(dest, "index.html"), encoding="utf-8").read()
    assert 'content="hosted"' in html
    assert 'src="static/js/app.js"' in html and 'src="/static' not in html
    for f in ("static/js/app.js", "static/css/arcjet.css", "static/img/logo-mark.png", ".nojekyll"):
        assert os.path.exists(os.path.join(dest, f)), f
