# NekoCafé DevOps PoC

实验三重点交付目录。该 Monorepo 包含两个核心服务：

- `services/reservation`：预约服务，Python 标准库实现，提供预约创建、查询、健康检查和指标。
- `services/member`：会员服务，Node.js 标准库实现，提供会员资料、隐私授权和指标。

## 为什么选择 Monorepo

两个服务处于同一课程实验阶段，共享 CI/CD、Compose、Helm 和观测配置。Monorepo 能让评审者一次 clone 即可在 30 分钟内运行完整 PoC；服务边界仍通过 Dockerfile、端口、健康检查和 Helm deployment 独立表达。

## 本地启动

```bash
make test
make up
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
curl http://localhost:8081/metrics
```

## 关键端口

| 组件 | 端口 | 说明 |
| --- | --- | --- |
| reservation | 8081 | 预约服务 |
| member | 8082 | 会员服务 |
| Prometheus | 9090 | 指标采集 |
| Grafana | 3000 | Dashboard，默认 admin/admin |

## 常用命令

```bash
make test      # Python unittest + Node test
make build     # 构建两个服务镜像
make up        # docker compose up -d --build
make down      # docker compose down -v
make scan      # Trivy 扫描 HIGH/CRITICAL
make rollback  # 本地展示回滚命令
```

## Secret 管理

`.env` 不提交仓库。CI/CD 使用 GitHub Secrets，K8s 使用 Secret 模板注入，应用通过环境变量读取。
