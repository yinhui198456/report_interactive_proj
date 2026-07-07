import json
from pathlib import Path

import pytest

import data_sources as ds

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def clean_config(monkeypatch):
    """Reset module-level config cache before and after each test."""
    monkeypatch.setattr(ds, "_config_cache", None)
    yield
    monkeypatch.setattr(ds, "_config_cache", None)


def test_load_config_reads_example_by_default(clean_config):
    config = ds.load_config()
    assert config["data_source"] == "seed"
    assert "neo4j" in config
    assert config["neo4j"]["uri"] == "bolt://localhost:7687"


def test_local_config_takes_precedence(clean_config, tmp_path, monkeypatch):
    local_dir = tmp_path / "data"
    local_dir.mkdir()
    local_config = local_dir / "config.local.json"
    local_config.write_text(
        json.dumps({"data_source": "neo4j", "neo4j": {"uri": "bolt://test:7687", "user": "u", "password": "secret", "database": "db"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(ds, "LOCAL_CONFIG_PATH", local_config)
    config = ds.load_config()
    assert config["data_source"] == "neo4j"
    assert config["neo4j"]["uri"] == "bolt://test:7687"


def test_default_data_source_is_seed(clean_config):
    assert ds.get_data_source_name() == "seed"


def test_seed_get_report_data(clean_config):
    data = ds.get_report_data()
    assert "project" in data
    assert "products" in data
    assert data["project"]["name"] == "江苏流域胃动力药Q3项目"
    assert isinstance(data["products"], list)
    assert len(data["products"]) > 0


def test_seed_get_project_data(clean_config):
    data = ds.get_project_data()
    assert data["name"] == "江苏流域胃动力药Q3项目"


def test_seed_get_products_data(clean_config):
    data = ds.get_products_data()
    assert isinstance(data, list)
    assert data[0]["name"] == "科赴 吗丁啉42s"


def test_check_neo4j_health_in_seed_mode(clean_config):
    health = ds.check_neo4j_health()
    assert health["enabled"] is False
    assert health["available"] is False
    assert "seed" in health["reason"].lower()


def test_check_neo4j_health_without_driver(clean_config, monkeypatch):
    monkeypatch.setattr(ds, "NEO4J_DRIVER_AVAILABLE", False)
    monkeypatch.setattr(ds, "_config_cache", {"data_source": "neo4j", "neo4j": {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "x", "database": "neo4j"}})
    health = ds.check_neo4j_health()
    assert health["enabled"] is True
    assert health["available"] is False
    assert "not installed" in health["reason"].lower()


def test_check_neo4j_health_does_not_expose_password(clean_config, monkeypatch):
    monkeypatch.setattr(ds, "NEO4J_DRIVER_AVAILABLE", False)
    monkeypatch.setattr(ds, "_config_cache", {"data_source": "neo4j", "neo4j": {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "super-secret", "database": "neo4j"}})
    health = ds.check_neo4j_health()
    health_text = json.dumps(health)
    assert "super-secret" not in health_text
