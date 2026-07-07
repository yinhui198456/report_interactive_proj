import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient

from main import (
    ALLOWED_STATE_FIELDS,
    STATE_PATH,
    app,
    default_state,
    load_seed,
    load_state,
    save_state,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_state(tmp_path, monkeypatch):
    isolated = tmp_path / "report_state.json"
    monkeypatch.setattr("main.STATE_PATH", isolated)
    save_state(default_state())


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "商销项目决策报告" in response.text


def test_api_report():
    response = client.get("/api/report")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "products" in data
    assert isinstance(data["products"], list)


def test_api_project():
    response = client.get("/api/project")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data


def test_api_products():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    names = [p["name"] for p in data if "name" in p]
    assert "科赴 吗丁啉42s" in names


def test_load_seed_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    try:
        load_seed(bad)
    except RuntimeError as e:
        assert "Invalid JSON" in str(e)
    else:
        raise AssertionError("Expected RuntimeError for invalid JSON")


def test_api_state_default():
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert data == default_state()


def test_api_project_save():
    project = {"name": "Test", "manager": "A", "region": "B", "period": "Q1", "budget": 10}
    response = client.post("/api/project", json=project)
    assert response.status_code == 200
    data = response.json()
    assert data["projectInfo"] == project
    response2 = client.get("/api/state")
    assert response2.json()["projectInfo"] == project


def test_api_policy_save():
    payload = {
        "projectPolicy": {"agreement": "x", "repCount": 2, "repCost": 1.0, "academicBudget": 5},
        "productList": [{"name": "a", "spec": "b"}],
    }
    response = client.post("/api/policy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["projectPolicy"]["agreement"] == "x"
    assert data["productList"][0]["name"] == "a"


def test_api_generate():
    response = client.post("/api/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == 1
    assert data["generated"] is True


def test_api_confirm():
    response = client.post("/api/confirm")
    assert response.status_code == 200
    data = response.json()
    assert data["confirmed"] is True


def test_api_put_state_filters_unknown():
    response = client.put(
        "/api/state",
        json={"phase": 2, "extra": "should-be-ignored", "projectInfo": {"name": "X"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == 2
    assert "extra" not in data
    assert set(data.keys()) == ALLOWED_STATE_FIELDS
    assert data["projectInfo"]["name"] == "X"


def test_api_reset_state():
    client.post("/api/generate")
    client.post("/api/confirm")
    response = client.post("/api/reset-state")
    assert response.status_code == 200
    assert response.json() == default_state()


def test_load_state_invalid_json(tmp_path):
    bad = tmp_path / "bad_state.json"
    bad.write_text("not json", encoding="utf-8")
    try:
        load_state(bad)
    except RuntimeError as e:
        assert "Invalid JSON" in str(e)
    else:
        raise AssertionError("Expected RuntimeError for invalid JSON")


def test_export_report_html():
    response = client.get("/api/export/report.html")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "project-report.html" in response.headers["content-disposition"]
    assert "江苏流域胃动力药Q3项目" in response.text
    assert "商品总数" in response.text


def test_export_products_csv():
    response = client.get("/api/export/products.csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "products.csv" in response.headers["content-disposition"]
    assert response.content.startswith(b"\xef\xbb\xbf")
    assert "id,name,spec" in response.text
    assert "科赴 吗丁啉42s" in response.text


def test_api_data_source_status_default():
    response = client.get("/api/data-source/status")
    assert response.status_code == 200
    data = response.json()
    assert data["data_source"] == "seed"
    assert data["neo4j"]["enabled"] is False
    assert data["neo4j"]["available"] is False


def test_api_neo4j_health_no_password():
    response = client.get("/api/neo4j/health")
    assert response.status_code == 200
    data = response.json()
    assert "password" not in str(data).lower()
    assert data["available"] is False


def test_api_report_still_returns_seed_data():
    response = client.get("/api/report")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "products" in data
    assert data["project"]["name"] == "江苏流域胃动力药Q3项目"


def test_api_products_still_contains_motilium():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    names = [p["name"] for p in data if "name" in p]
    assert "科赴 吗丁啉42s" in names


def test_import_from_non_project_cwd():
    workspace_root = Path(__file__).resolve().parent.parent.parent
    result = subprocess.run(
        [sys.executable, "-c", "from report_interactive_proj.main import app; print('ok')"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
