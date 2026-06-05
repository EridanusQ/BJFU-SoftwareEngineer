# NekoCafé DevOps PoC Runbook

本运行手册用于指导实验三 D3-2 仓库的本地启动、验证、排障和证据截图。执行前请确认当前目录为 `D3-2_源代码与配置仓库`。

## 1. 启动前检查

1. 确认 Docker Desktop 已启动，并且 `docker version` 能正常返回客户端与服务端信息。
2. 确认当前端口未被占用：`8081`、`8082`、`9090`、`3001`。
3. 确认 Python 与 Node.js 可用：

```bash
python --version
node --version
npm --version
```

4. 如果要执行镜像扫描，确认本机已安装 Trivy，或准备使用 Docker 方式运行 Trivy。

## 2. 本地测试

```bash
make test
```

该命令会执行 reservation 的 Python 单元测试和 member 的 Node.js 测试。测试失败时先不要启动容器，应根据失败日志修复业务逻辑或测试数据。

Windows PowerShell 中如无法使用 `make`，可分别执行：

```powershell
python -m unittest discover -s services/reservation/tests -v
npm test --prefix services/member
```

## 3. 启动服务

```bash
make up
```

该命令会执行 `docker compose up -d --build`，构建并启动以下组件：

- reservation：预约服务，对外端口 `8081`。
- member：会员服务，对外端口 `8082`。
- redis：预约锁和缓存能力预留。
- postgres：未来持久化能力预留。
- prometheus：指标采集，对外端口 `9090`。
- grafana：Dashboard，对外端口 `3001`。

启动后可查看容器状态：

```bash
docker compose ps
```

## 4. 接口验证

```bash
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
curl http://localhost:8081/metrics
curl http://localhost:8082/metrics
```

健康检查应返回正常状态，指标端点应返回 Prometheus 文本格式数据。如果 `/metrics` 有数据但 Grafana 无图表，优先检查 Prometheus targets。

## 5. 监控验证

1. 打开 `http://localhost:9090/targets`，确认 reservation 和 member 为 `UP`。
2. 打开 `http://localhost:3001`，进入 NekoCafé DevOps Dashboard。
3. 如果需要登录，使用 `admin/admin`；仓库配置中也开启了匿名只读访问。
4. 观察请求量、错误率、延迟、资源使用等面板是否出现数据。

## 6. 常见排障

服务未启动：

```bash
docker compose ps
docker compose logs reservation member
```

端口被占用：释放本机端口，或临时修改 `docker-compose.yml` 中的端口映射。

Prometheus 无数据：检查 `config/prometheus/prometheus.yml` 中 target 名称是否与 Compose 服务名一致，并确认服务容器健康。

Grafana 无 Dashboard：检查 Grafana 容器日志，确认 `config/grafana/provisioning` 和 `config/grafana/dashboards` 已正确挂载。

CI 与本地结果不一致：先在本地运行 `make test` 和 `make build`，再查看 GitHub Actions 日志中失败的具体步骤，重点检查依赖版本、基础镜像和缓存。

## 7. 停止与清理

```bash
make down
```

该命令会执行 `docker compose down -v`，同时清理数据卷。若只想暂停演示环境并保留数据，可执行：

```bash
docker compose stop
```

## 8. 截图建议

- `docker compose ps`：证明本地容器已启动。
- `/healthz` 或 `/metrics`：证明服务接口可访问。
- Prometheus targets：证明指标采集正常。
- Grafana Dashboard：证明可观测性链路可用。
