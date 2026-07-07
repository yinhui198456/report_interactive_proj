# 仓库边界说明

## 项目目录

本项目根目录：

```
/opt/personal-agent-workspace/report_interactive_proj
```

## 工作区与仓库关系

`/opt/personal-agent-workspace` 是共享工作区根目录，包含多个独立项目。工作区根目录的 `.git` 是历史遗留/聚合用途，**不等同于**本项目的 Git 仓库边界。

每个一级子项目原则上对应独立的 GitHub 仓库。

## 创建独立 GitHub 仓库

在项目目录内执行：

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
gh repo create report_interactive_proj --private --source=. --remote=report-interactive
```

或者创建公开仓库：

```bash
gh repo create report_interactive_proj --public --source=. --remote=report-interactive
```

## 从工作区根目录推送单项目

如果仍从工作区根目录操作，优先使用 `git subtree push`，避免把其他项目文件带入本仓库：

```bash
cd /opt/personal-agent-workspace
git subtree push --prefix=report_interactive_proj report-interactive main
```

## 推送前检查

执行任何推送前，必须核对 remote：

```bash
git remote -v
```

## 禁止操作

- **不要**在未确认 remote 时执行 `git push origin`。
- **不要**把本项目文件推送到 `resume-jd-scorer` 或其它项目仓库。
- **不要**在 `git remote -v` 显示 `origin` 指向其他项目时直接推送。

## 提交内容注意

- 不要提交真实 Neo4j 密码。
- 不要提交 `data/config.local.json`。
- 不要提交 `__pycache__/`、`.pytest_cache/`、`* .pyc`。
