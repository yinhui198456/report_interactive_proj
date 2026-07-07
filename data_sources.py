import json
from pathlib import Path

try:
    from neo4j import GraphDatabase

    NEO4J_DRIVER_AVAILABLE = True
except ImportError:
    GraphDatabase = None
    NEO4J_DRIVER_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent
EXAMPLE_CONFIG_PATH = BASE_DIR / "config.example.json"
LOCAL_CONFIG_PATH = BASE_DIR / "data" / "config.local.json"
SEED_PATH = BASE_DIR / "data" / "report_seed.json"

_config_cache = None


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in config file {path}: {e}") from e


def load_config(path: Path | None = None) -> dict:
    """Load configuration.

    If a specific path is provided, load only that file.
    Otherwise merge LOCAL_CONFIG_PATH over EXAMPLE_CONFIG_PATH.
    """
    global _config_cache
    if path is None and _config_cache is not None:
        return _config_cache

    if path is not None:
        return _load_json(path)

    config = _load_json(EXAMPLE_CONFIG_PATH)
    local_config = _load_json(LOCAL_CONFIG_PATH)
    if local_config:
        config = _deep_merge(config, local_config)

    # Ensure defaults are present
    config.setdefault("data_source", "seed")
    config.setdefault("neo4j", {
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "change-me",
        "database": "neo4j",
    })

    _config_cache = config
    return config


def get_data_source_name() -> str:
    return load_config().get("data_source", "seed")


def load_seed(path: Path | None = None) -> dict:
    path = path or SEED_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"Seed data not found: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in seed data: {e}") from e


def get_report_data() -> dict:
    seed = load_seed()
    return {
        "project": seed.get("project", {}),
        "products": seed.get("products", []),
    }


def get_project_data() -> dict:
    return load_seed().get("project", {})


def get_products_data() -> list:
    return load_seed().get("products", [])


def check_neo4j_health() -> dict:
    config = load_config()
    data_source = config.get("data_source", "seed")

    if data_source != "neo4j":
        return {
            "enabled": False,
            "available": False,
            "reason": "data_source is seed",
        }

    if not NEO4J_DRIVER_AVAILABLE:
        return {
            "enabled": True,
            "available": False,
            "reason": "neo4j driver is not installed",
        }

    neo4j_config = config.get("neo4j", {})
    uri = neo4j_config.get("uri")
    user = neo4j_config.get("user")
    password = neo4j_config.get("password")

    if not uri or not user or password is None:
        return {
            "enabled": True,
            "available": False,
            "reason": "neo4j configuration is incomplete",
        }

    driver = None
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=neo4j_config.get("database") or "neo4j") as session:
            session.run("RETURN 1 AS ok")
        return {
            "enabled": True,
            "available": True,
            "reason": "connected",
        }
    except Exception as e:
        return {
            "enabled": True,
            "available": False,
            "reason": f"neo4j connection failed: {e}",
        }
    finally:
        if driver is not None:
            try:
                driver.close()
            except Exception:
                pass
