from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def req_text():
    path = BASE_DIR / "requirements.txt"
    assert path.exists(), "requirements.txt should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def run_sh_text():
    path = BASE_DIR / "run.sh"
    assert path.exists(), "run.sh should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def service_text():
    path = BASE_DIR / "deploy" / "systemd" / "report-interactive.service.example"
    assert path.exists(), "systemd example should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def deployment_md_text():
    path = BASE_DIR / "docs" / "DEPLOYMENT.md"
    assert path.exists(), "DEPLOYMENT.md should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def repository_md_text():
    path = BASE_DIR / "docs" / "REPOSITORY.md"
    assert path.exists(), "REPOSITORY.md should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def gitignore_text():
    path = BASE_DIR / ".gitignore"
    assert path.exists(), ".gitignore should exist"
    return path.read_text(encoding="utf-8")


def test_requirements_exists(req_text):
    assert "fastapi" in req_text.lower()
    assert "uvicorn" in req_text.lower()
    assert "pytest" in req_text.lower()


def test_requirements_does_not_require_neo4j(req_text):
    lines = [line.strip().lower() for line in req_text.splitlines()]
    package_lines = [line for line in lines if line and not line.startswith("#")]
    assert not any("neo4j" in line for line in package_lines)


def test_run_sh_exists_and_runs_uvicorn(run_sh_text):
    assert "python3 -m uvicorn main:app" in run_sh_text


def test_run_sh_uses_host_and_port_env_vars(run_sh_text):
    assert "${HOST" in run_sh_text or "$HOST" in run_sh_text
    assert "${PORT" in run_sh_text or "$PORT" in run_sh_text


def test_run_sh_has_shebang(run_sh_text):
    assert run_sh_text.startswith("#!/bin/bash") or run_sh_text.startswith("#!/usr/bin/env bash")


def test_systemd_example_contains_key_directives(service_text):
    assert "WorkingDirectory=" in service_text
    assert "ExecStart=" in service_text
    assert "Restart=on-failure" in service_text


def test_systemd_example_points_to_project_paths(service_text):
    assert "/opt/personal-agent-workspace/report_interactive_proj" in service_text


def test_deployment_md_contains_key_sections(deployment_md_text):
    assert "health" in deployment_md_text.lower()
    assert "systemctl" in deployment_md_text.lower()
    assert "journalctl" in deployment_md_text.lower()


def test_deployment_md_warns_against_committing_local_config(deployment_md_text):
    assert "config.local.json" in deployment_md_text


def test_repository_md_contains_subtree_push(repository_md_text):
    assert "git subtree push" in repository_md_text


def test_repository_md_warns_against_git_push_origin(repository_md_text):
    assert "git push origin" in repository_md_text


def test_gitignore_excludes_local_config(gitignore_text):
    assert "data/config.local.json" in gitignore_text
