from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture
def dry_run_md_text():
    path = BASE_DIR / "docs" / "PUBLISH_DRY_RUN.md"
    assert path.exists(), "PUBLISH_DRY_RUN.md should exist"
    return path.read_text(encoding="utf-8")


@pytest.fixture
def dry_run_script_text():
    path = BASE_DIR / "scripts" / "publish-dry-run.sh"
    if not path.exists():
        pytest.skip("publish-dry-run.sh not created")
    return path.read_text(encoding="utf-8")


def test_publish_dry_run_md_has_required_sections(dry_run_md_text):
    assert "Verification Results" in dry_run_md_text
    assert "Git Boundary Check" in dry_run_md_text
    assert "Suggested Commands" in dry_run_md_text


def test_publish_dry_run_md_contains_subtree_push(dry_run_md_text):
    assert "git subtree push --prefix=report_interactive_proj" in dry_run_md_text


def test_publish_dry_run_md_warns_against_git_push_origin(dry_run_md_text):
    text = dry_run_md_text
    assert "git push origin" in text
    assert any(marker in text for marker in ["禁止", "不要执行", "不要", "未确认"])


def test_publish_dry_run_script_does_not_execute_git_push(dry_run_script_text):
    for line in dry_run_script_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "git push" in stripped:
            assert "echo" in stripped, f"Line appears to execute git push: {line}"
