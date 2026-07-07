# 商销项目决策报告 Web 服务

将静态 HTML 报告包装为独立 FastAPI 服务，可通过 HTTP 访问。当前数据来自后端 JSON seed 文件，状态持久化为本地 JSON 文件；已预留 Neo4j 数据源接入骨架，但未要求真实 Neo4j 业务查询替换。

## 安装依赖

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
python3 -m pip install -r requirements.txt
```

## 启动

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
./run.sh
```

默认监听 `0.0.0.0:8010`。指定端口：

```bash
PORT=8011 ./run.sh
```

开发热重载（可选）：

```bash
uvicorn main:app --host 0.0.0.0 --port 8010 --reload
```

## 访问

- 报告首页：`http://localhost:8010/`
- 健康检查：`http://localhost:8010/health`
- 静态文件：`http://localhost:8010/static/`

## Seed 数据 API

- 完整报告数据：`GET /api/report`
  - 返回：`{"project": {...}, "products": [...]}`
- 项目信息：`GET /api/project`
- 商品列表：`GET /api/products`

## 状态 API

运行态状态保存在 `data/report_state.json`。

- 获取当前状态：`GET /api/state`
- 覆盖保存状态：`PUT /api/state`
  - 只允许字段：`phase`、`projectInfo`、`projectPolicy`、`productList`、`generated`、`confirmed`
- 保存项目信息：`POST /api/project`
- 保存政策与商品清单：`POST /api/policy`
- 标记报告已生成：`POST /api/generate`
- 确认项目启动：`POST /api/confirm`
- 重置为默认状态：`POST /api/reset-state`（仅用于开发/测试）

## 导出 API

当前使用 HTML/CSV 实现，尚未生成真正 PDF/XLSX，后续可升级。

- 导出打印版报告：`GET /api/export/report.html`
  - 返回 `text/html; charset=utf-8`
  - 下载文件名：`project-report.html`
- 导出商品清单：`GET /api/export/products.csv`
  - 返回 `text/csv; charset=utf-8`（UTF-8 with BOM）
  - 下载文件名：`products.csv`

## 数据源

- `data/report_seed.json`：项目与商品 seed 数据
- `data/report_state.json`：运行态状态

## 数据源配置

默认使用 `data/report_seed.json`，无需 Neo4j 即可运行。

配置文件：
- `config.example.json`：默认/示例配置，`data_source` 为 `"seed"`
- `data/config.local.json`：可选本地覆盖配置，适合存放真实 Neo4j 连接信息（已加入 `.gitignore`，**不要提交**）

`data_source` 支持：
- `"seed"`（默认）：使用本地 JSON seed 数据
- `"neo4j"`：启用 Neo4j 连接骨架（本阶段业务数据仍降级使用 seed）

当前 Neo4j 阶段仅完成连接健康检查和接入骨架：
- `GET /api/data-source/status`：查看当前数据源与 Neo4j 状态
- `GET /api/neo4j/health`：查看 Neo4j 健康检查结果（不暴露密码）

如需启用真实 Neo4j，请：
1. 安装 neo4j Python driver：`pip install neo4j`
2. 创建 `data/config.local.json`，设置 `data_source: "neo4j"` 和连接信息
3. 重启服务

## 前端状态与 XSS 防护

- 前端状态优先通过 `/api/state` 等后端 API 持久化；后端不可用时自动降级到 `localStorage`（键名 `proj_report_v5`）。
- `escapeHtml()` 使用 DOM `textContent` 对动态文本进行 HTML 转义，所有 seed/用户输入（项目名称、周期、预算、商品名、规格等）在插入 `innerHTML` 前均经过转义。
- 提供 `resetDemoState()` 一键重置：清除后端状态并移除 `localStorage` 本地缓存。
- 导出按钮调用真实后端端点 `/api/export/report.html` 与 `/api/export/products.csv`，通过 `downloadFile()` 触发浏览器下载。

## 部署与仓库

- 部署说明：`docs/DEPLOYMENT.md`
- 仓库边界与推送规范：`docs/REPOSITORY.md`
- 首版发布检查清单：`docs/RELEASE_CHECKLIST.md`

## 当前能力

- 静态报告页面服务
- Seed 数据 API：`/api/report`、`/api/project`、`/api/products`
- 状态持久化 API：`/api/state`、`/api/project`、`/api/policy`、`/api/generate`、`/api/confirm`、`/api/reset-state`
- HTML/CSV 导出：`/api/export/report.html`、`/api/export/products.csv`
- 前端 `localStorage` 降级、状态提示、XSS 转义
- Neo4j 数据源接入骨架与健康检查：`/api/data-source/status`、`/api/neo4j/health`

## 测试

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
pytest -q
```
