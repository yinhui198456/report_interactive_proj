import csv
import io
from html import escape


def build_html_report(seed: dict, state: dict) -> str:
    """Build a printable HTML report from seed and state."""
    project = seed.get("project", {})
    products = seed.get("products", [])

    project_rows = "\n".join(
        f"        <tr><th>{escape(key)}</th><td>{escape(str(value))}</td></tr>"
        for key, value in project.items()
    )

    product_rows = "\n".join(
        "        <tr>"
        + "".join(f"<td>{escape(str(p.get(k, '')))}</td>" for k in _PRODUCT_COLUMNS)
        + "</tr>"
        for p in products
    )

    generated = "是" if state.get("generated") else "否"
    confirmed = "是" if state.get("confirmed") else "否"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{escape(project.get('name', '项目报告'))}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 2rem; color: #222; }}
    h1 {{ font-size: 1.6rem; margin-bottom: .5rem; }}
    h2 {{ font-size: 1.2rem; margin-top: 1.5rem; border-bottom: 1px solid #ddd; padding-bottom: .3rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: .5rem; }}
    th, td {{ border: 1px solid #ccc; padding: .5rem; text-align: left; font-size: .85rem; }}
    th {{ background: #f5f5f5; }}
    .meta {{ color: #666; margin-bottom: 1rem; }}
    .status {{ margin-top: 1rem; }}
    @media print {{
      body {{ margin: 1cm; }}
      h2 {{ page-break-after: avoid; }}
      tr {{ page-break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <h1>{escape(project.get('name', '项目报告'))}</h1>
  <p class="meta">负责人：{escape(project.get('manager', ''))} | 目标区域：{escape(project.get('region', ''))} | 项目周期：{escape(project.get('period', ''))} | 预算：{escape(str(project.get('budget', '')))} 万元</p>

  <h2>项目信息</h2>
  <table>
    <tbody>
{project_rows}
    </tbody>
  </table>

  <h2>状态摘要</h2>
  <p class="status">商品总数：{len(products)} | 报告已生成：{generated} | 项目已确认：{confirmed}</p>

  <h2>商品列表</h2>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>名称</th>
        <th>规格</th>
        <th>品类</th>
        <th>供应价</th>
        <th>零售价</th>
        <th>毛利率</th>
        <th>医保</th>
        <th>集采</th>
        <th>月销量</th>
        <th>概要</th>
      </tr>
    </thead>
    <tbody>
{product_rows}
    </tbody>
  </table>
</body>
</html>"""


_PRODUCT_COLUMNS = [
    "id",
    "name",
    "spec",
    "category",
    "supplyPrice",
    "retail",
    "margin",
    "insurance",
    "procurement",
    "monthlyVol",
    "summary",
]


def build_products_csv(seed: dict) -> str:
    """Build a UTF-8 with BOM CSV string of products."""
    products = seed.get("products", [])
    output = io.StringIO()
    output.write("﻿")
    writer = csv.writer(output)
    writer.writerow(_PRODUCT_COLUMNS)
    for p in products:
        writer.writerow([p.get(k, "") for k in _PRODUCT_COLUMNS])
    return output.getvalue()
