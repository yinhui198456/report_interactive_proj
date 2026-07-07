# 部署说明

## 本地启动

```bash
cd /opt/personal-agent-workspace/report_interactive_proj
python3 -m pip install -r requirements.txt
./run.sh
```

默认监听 `0.0.0.0:8010`。

## 指定端口

```bash
PORT=8011 ./run.sh
```

## 测试

```bash
pytest -q
```

## 健康检查

```bash
curl http://localhost:8010/health
```

## 数据源状态

```bash
curl http://localhost:8010/api/data-source/status
```

## systemd 部署

1. 复制示例 service 文件到系统目录：

```bash
sudo cp deploy/systemd/report-interactive.service.example /etc/systemd/system/report-interactive.service
```

2. 编辑 `/etc/systemd/system/report-interactive.service`，按实际环境修改 `User`/`Group`。

3. 重载并启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now report-interactive
```

4. 查看日志：

```bash
sudo journalctl -u report-interactive -f
```

## Nginx 反代（可选）

参考 `deploy/nginx/report-interactive.nginx.example`，修改 `server_name` 后放到 `/etc/nginx/sites-available/` 并启用。

## Neo4j 可选配置

1. 安装 neo4j Python driver：

```bash
python3 -m pip install neo4j
```

2. 创建 `data/config.local.json`：

```json
{
  "data_source": "neo4j",
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "your-real-password",
    "database": "neo4j"
  }
}
```

**注意**：`data/config.local.json` 已加入 `.gitignore`，**不要提交到 Git**，也不要写入真实密码到 `config.example.json`。

3. 重启服务后访问：

```bash
curl http://localhost:8010/api/neo4j/health
```

当前 Neo4j 阶段仅完成连接健康检查和接入骨架，业务数据仍降级使用 `data/report_seed.json`。
