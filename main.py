import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

try:
    from .exporters import build_html_report, build_products_csv
except ImportError:
    from exporters import build_html_report, build_products_csv

try:
    from .data_sources import (
        check_neo4j_health,
        get_data_source_name,
        get_products_data,
        get_project_data,
        get_report_data,
    )
except ImportError:
    from data_sources import (
        check_neo4j_health,
        get_data_source_name,
        get_products_data,
        get_project_data,
        get_report_data,
    )

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
SEED_PATH = DATA_DIR / "report_seed.json"
STATE_PATH = DATA_DIR / "report_state.json"

ALLOWED_STATE_FIELDS = {
    "phase",
    "projectInfo",
    "projectPolicy",
    "productList",
    "generated",
    "confirmed",
}


def load_seed(path: Path | None = None) -> dict:
    """Load report seed data from JSON."""
    path = path or SEED_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"Seed data not found: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in seed data: {e}") from e


def default_state() -> dict:
    return {
        "phase": 0,
        "projectInfo": None,
        "projectPolicy": None,
        "productList": [],
        "generated": False,
        "confirmed": False,
    }


def load_state(path: Path | None = None) -> dict:
    """Load persisted state from JSON. Returns default state if file is missing."""
    path = path or STATE_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = default_state()
        save_state(data, path=path)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in state file: {e}") from e

    if not isinstance(data, dict):
        raise RuntimeError("State file must contain a JSON object")

    state = default_state()
    for key in ALLOWED_STATE_FIELDS:
        if key in data:
            state[key] = data[key]
    return state


def save_state(state: dict, path: Path | None = None) -> dict:
    """Save state to JSON, filtering unknown fields."""
    path = path or STATE_PATH
    filtered = {k: v for k, v in state.items() if k in ALLOWED_STATE_FIELDS}
    full = default_state()
    full.update(filtered)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(full, f, ensure_ascii=False, indent=2)
    except OSError as e:
        raise RuntimeError(f"Failed to write state file: {e}") from e
    return full


def _load_state() -> dict:
    try:
        return load_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _save_state(state: dict) -> dict:
    try:
        return save_state(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app = FastAPI(title="商销项目决策报告服务")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/report")
def api_report() -> dict:
    return get_report_data()


@app.get("/api/project")
def api_project() -> dict:
    return get_project_data()


@app.get("/api/products")
def api_products() -> list:
    return get_products_data()


@app.get("/api/export/report.html")
def api_export_report_html() -> Response:
    seed = get_report_data()
    state = _load_state()
    html = build_html_report(seed, state)
    return Response(
        content=html,
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="project-report.html"'},
    )


@app.get("/api/export/products.csv")
def api_export_products_csv() -> Response:
    seed = get_report_data()
    csv_text = build_products_csv(seed)
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="products.csv"'},
    )


@app.get("/api/data-source/status")
def api_data_source_status() -> dict:
    return {
        "data_source": get_data_source_name(),
        "neo4j": check_neo4j_health(),
    }


@app.get("/api/neo4j/health")
def api_neo4j_health() -> dict:
    return check_neo4j_health()


@app.get("/api/state")
def api_state() -> dict:
    return _load_state()


@app.put("/api/state")
def api_put_state(new_state: dict) -> dict:
    return _save_state(new_state)


@app.post("/api/project")
def api_post_project(project_info: dict) -> dict:
    state = _load_state()
    state["projectInfo"] = project_info
    return _save_state(state)


@app.post("/api/policy")
def api_post_policy(body: dict) -> dict:
    state = _load_state()
    state["projectPolicy"] = body.get("projectPolicy")
    state["productList"] = body.get("productList", [])
    return _save_state(state)


@app.post("/api/generate")
def api_generate() -> dict:
    state = _load_state()
    state["phase"] = 1
    state["generated"] = True
    return _save_state(state)


@app.post("/api/confirm")
def api_confirm() -> dict:
    state = _load_state()
    state["confirmed"] = True
    return _save_state(state)


@app.post("/api/reset-state")
def api_reset_state() -> dict:
    return _save_state(default_state())


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
