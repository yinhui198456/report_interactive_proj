import os
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def checklist_text():
    path = BASE_DIR / "docs" / "RELEASE_CHECKLIST.md"
    assert path.exists(), "RELEASE_CHECKLIST.md should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def gitignore_text():
    path = BASE_DIR / ".gitignore"
    assert path.exists(), ".gitignore should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def run_sh_path():
    return BASE_DIR / "run.sh"


def test_release_checklist_exists(checklist_text):
    assert "Files To Include" in checklist_text
    assert "Files Never To Commit" in checklist_text
    assert "Repository Boundary" in checklist_text


def test_gitignore_excludes_local_config(gitignore_text):
    assert "data/config.local.json" in gitignore_text


def test_gitignore_excludes_env_and_logs(gitignore_text):
    assert ".env" in gitignore_text
    assert "*.log" in gitignore_text


def test_gitignore_excludes_caches(gitignore_text):
    assert ".pytest_cache/" in gitignore_text
    assert "__pycache__/" in gitignore_text
    assert "*.pyc" in gitignore_text


def test_gitignore_does_not_exclude_seed(gitignore_text):
    assert "data/report_seed.json" not in gitignore_text


def test_run_sh_is_executable(run_sh_path):
    assert run_sh_path.exists()
    assert os.access(run_sh_path, os.X_OK)


def test_local_config_does_not_exist():
    assert not (BASE_DIR / "data" / "config.local.json").exists()
