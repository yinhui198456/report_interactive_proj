from pathlib import Path

import pytest

HTML_PATH = Path(__file__).resolve().parent.parent / "static" / "index.html"


@pytest.fixture
def html():
    return HTML_PATH.read_text(encoding="utf-8")


def test_escapeHtml_exists(html):
    assert "function escapeHtml" in html


def test_saveLocalState_exists(html):
    assert "function saveLocalState" in html


def test_saveRemoteState_exists(html):
    assert "function saveRemoteState" in html


def test_resetDemoState_exists(html):
    assert "function resetDemoState" in html


def test_export_buttons_use_real_endpoints(html):
    assert "/api/export/report.html" in html
    assert "/api/export/products.csv" in html


def test_old_demo_export_alerts_removed(html):
    assert "导出PDF报告（演示功能）" not in html
    assert "导出客户清单Excel（演示功能）" not in html


def test_renderProductList_escapes_inputs(html):
    func = html.split("function renderProductList(")[1].split("function ")[0]
    assert "escapeHtml" in func


def test_sidebar_product_name_escaped(html):
    func = html.split("function renderSidebar(")[1].split("function ")[0]
    assert "escapeHtml" in func


def test_dashboard_project_name_escaped(html):
    func = html.split("function buildDashboard(")[1].split("function ")[0]
    assert "escapeHtml" in func


def test_toast_or_status_area_exists(html):
    assert any(tag in html for tag in ["id=\"toast\"", "id=\"statusToast\"", "class=\"toast\""])
