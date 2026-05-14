# NekoCafé Runbook

## 本地启动

1. 确认 Docker Desktop 已启动。
2. 执行 `make up`。
3. 访问 `http://localhost:8081/healthz` 和 `http://localhost:8082/healthz`。
4. 访问 Prometheus `http://localhost:9090`，Grafana `http://localhost:3000`。

## 常见排障

- 服务不健康：`docker compose logs reservation member`。
- 端口占用：修改 compose 端口映射或释放 8081/8082。
- 指标无数据：检查 Prometheus targets 是否 UP。
- CI 失败：先本地执行 `make test`，再执行 `make build`。
