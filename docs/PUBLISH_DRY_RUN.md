# 独立仓库发布前 Dry-Run 报告

## Verification Results

### 测试

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
pytest -q
```

结果：待最终执行后回填。

### 工作区根目录导入

```bash
cd /opt/personal-agent-workspace
python3 -c "import report_interactive_proj.main; print('ok')"
```

结果：`ok`

### run.sh 服务验证

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
PORT=8023 ./run.sh
```

```bash
curl http://localhost:8023/health
```

结果：`{"status":"ok"}`

```bash
curl http://localhost:8023/api/data-source/status
```

结果：`{"data_source":"seed","neo4j":{"enabled":false,"available":false,"reason":"data_source is seed"}}`

### 缓存清理

已清理项目内 `__pycache__/`、`.pytest_cache/`、`* .pyc`。

## Files Planned For First Release

首版计划纳入仓库的文件/目录：

- `main.py`
- `data_sources.py`
- `exporters.py`
- `static/index.html`
- `data/report_seed.json`
- `data/report_state.json`
- `config.example.json`
- `requirements.txt`
- `run.sh`
- `README.md`
- `docs/`
- `deploy/`
- `tests/`
- `scripts/`
- `neo4j_report_interactive_proj_20260626_100456.html`

## Files Excluded

以下内容禁止提交：

- `data/config.local.json`
- `.env`
- `*.log`
- `__pycache__/`
- `.pytest_cache/`
- `*.pyc`
- 真实 Neo4j 密码
- GitHub token 或个人凭证

## Git Boundary Check

- 工作区根目录 `/opt/personal-agent-workspace` 是共享聚合目录，不等同于本项目独立仓库。
- 当前 remote 状态：
  - `origin` 指向 `yinhui198456/resume-jd-scorer`（其他项目仓库）
  - `report-interactive` 指向 `yinhui198456/report_interactive_proj`（本项目仓库）
- 推送前必须执行 `git remote -v` 确认 remote。
- **禁止**在未确认 remote 时执行 `git push origin`。
- 本 dry-run **未执行** `git push`、`gh repo create`、`git commit`，也**未修改**任何 remote。

## Suggested Commands After User Confirmation

> ⚠️ 以下命令仅作为建议，**必须等用户确认后才能执行**。

### 方案 A：在项目目录创建独立仓库

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
git init
git add .
git commit -m "feat: add interactive report web service

Co-Authored-By: Claude <noreply@anthropic.com>"
gh repo create report_interactive_proj --private --source=. --remote=report-interactive
git push -u report-interactive main
```

### 方案 B：从工作区根目录使用 subtree 推送

```bash
cd /opt/personal-agent-workspace
git remote -v
git subtree push --prefix=report_interactive_proj report-interactive main
```

推荐优先使用方案 A，使项目拥有独立的 `.git` 历史，避免与工作区其它项目混在一起。
