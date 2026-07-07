from pathlib import Path

import pytest

from exporters import build_html_report, build_products_csv


@pytest.fixture
def sample_seed():
    return {
        "project": {
            "name": "江苏流域胃动力药Q3项目",
            "manager": "张三",
            "region": "江苏",
            "period": "2026年Q3",
            "budget": 50,
        },
        "products": [
            {
                "id": "p1",
                "name": "科赴 吗丁啉42s",
                "spec": "10mg×42片/盒",
                "category": "胃动力药",
                "supplyPrice": 23.5,
                "retail": 30.0,
                "margin": "27.7%",
                "insurance": "医保乙类",
                "procurement": "非集采",
                "monthlyVol": 13200,
                "summary": "月均 13,200 盒",
            }
        ],
    }


def test_build_html_report_contains_project_info(sample_seed):
    html = build_html_report(sample_seed, {"generated": True, "confirmed": False})
    assert "江苏流域胃动力药Q3项目" in html
    assert "商品总数" in html
    assert "科赴 吗丁啉42s" in html


def test_build_html_report_escapes_html(sample_seed):
    seed = sample_seed.copy()
    seed["project"] = {**sample_seed["project"], "name": "Test <script>"}
    html = build_html_report(seed, {})
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_build_products_csv(sample_seed):
    csv_text = build_products_csv(sample_seed)
    assert csv_text.startswith("﻿")
    assert "id,name,spec" in csv_text
    assert "科赴 吗丁啉42s" in csv_text
    assert "胃动力药" in csv_text
