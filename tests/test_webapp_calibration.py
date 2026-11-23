"""Calibration endpoints of the web interface."""

import os
from pathlib import Path

import pytest

pytest.importorskip("flask")

from arcjetCV.webapp.server import app  # noqa: E402

IMAGE = str(Path(__file__).resolve().parent / "arcjetcv_calibration.jpg")


@pytest.fixture
def client():
    return app.test_client()


def test_pattern_measures_pixels_per_mm(client):
    r = client.post(
        "/api/calibration/pattern",
        json={"path": IMAGE, "cols": 4, "rows": 9, "diagonal_mm": 100},
    )
    assert r.status_code == 200, r.json
    j = r.json
    assert j["pattern_type"]
    assert j["diagonal_px"] > 0
    assert j["pixels_per_mm"] == pytest.approx(j["diagonal_px"] / 100)
    assert j["image"].startswith("data:image/jpeg;base64,")
    assert "camera_matrix" in j["calibration"]


def test_pattern_wrong_size_reports_error(client):
    r = client.post("/api/calibration/pattern", json={"path": IMAGE, "cols": 5, "rows": 5})
    assert r.status_code == 400
    assert "No pattern detected" in r.json["error"]


def test_save_then_load_round_trip(client, tmp_path):
    data = {"pixels_per_mm": 12.5, "pattern_size": [4, 9]}
    r = client.post(
        "/api/calibration/save",
        json={"path": str(tmp_path / "calib"), "calibration": data},
    )
    assert r.status_code == 200, r.json
    path = r.json["path"]
    assert path.endswith(".json") and os.path.exists(path)

    r = client.post("/api/calibration/load", json={"path": path})
    assert r.status_code == 200, r.json
    assert r.json["pixels_per_mm"] == 12.5
    assert r.json["has_camera_model"] is False


def test_load_rejects_unrelated_json(client, tmp_path):
    p = tmp_path / "other.json"
    p.write_text('{"foo": 1}')
    r = client.post("/api/calibration/load", json={"path": str(p)})
    assert r.status_code == 400


def test_image_endpoint_and_browse(client):
    r = client.post("/api/calibration/image", json={"path": IMAGE})
    assert r.status_code == 200
    assert r.json["width"] > 0 and r.json["height"] > 0

    r = client.get("/api/browse", query_string={"kind": "image", "path": os.path.dirname(IMAGE)})
    names = [e["name"] for e in r.json["entries"] if e["type"] == "file"]
    assert "arcjetcv_calibration.jpg" in names
