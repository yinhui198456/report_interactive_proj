# 首版发布/提交清单

## Pre-commit Checks

- [ ] `cd /opt/personal-agent-workspace/report_interactive_proj && pytest -q`
- [ ] `cd /opt/personal-agent-workspace && python3 -c "import report_interactive_proj.main; print('ok')"`
- [ ] `./run.sh` 启动后访问：`curl http://localhost:8010/health`
- [ ] `./run.sh` 启动后访问：`curl http://localhost:8010/api/data-source/status`
- [ ] 确认项目目录内无 `__pycache__/`、`.pytest_cache/`、`* .pyc`

## Files To Include

首版仓库应包含以下文件/目录：

- `main.py` — FastAPI 应用入口
- `data_sources.py` — 数据源切换层
- `exporters.py` — HTML/CSV 导出
- `static/index.html` — 前端单页应用
- `data/report_seed.json` — 项目与商品 seed 数据
- `data/report_state.json` — 默认运行态状态
- `config.example.json` — 示例配置
- `requirements.txt` — 项目级依赖
- `run.sh` — 启动脚本
- `README.md` — 项目说明
- `docs/` — 部署、仓库边界、发布清单文档
- `deploy/` — systemd/nginx 示例
- `tests/` — 测试文件
- `neo4j_report_interactive_proj_20260626_100456.html` — 原始静态报告归档

## Files Never To Commit

以下内容**禁止**提交到仓库：

- `data/config.local.json`（真实连接信息，已加入 `.gitignore`）
- `.env`
- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`
- 真实 Neo4j 密码
- 任何 GitHub token 或个人凭证

## Repository Boundary

- 本项目应对应独立的 GitHub 仓库，例如 `yinhui198456/report_interactive_proj`。
- 推送前必须执行 `git remote -v`，确认 remote 指向本项目仓库。
- **禁止**在未确认 remote 时执行 `git push origin`。
- 如果从工作区根目录聚合仓库推送单项目，优先使用 subtree：

```bash
cd /opt/personal-agent-workspace
git subtree push --prefix=report_interactive_proj report-interactive main
```

## Suggested First Commit Message

```
feat: add interactive report web service

Co-Authored-By: Claude <noreply@anthropic.com>
```
