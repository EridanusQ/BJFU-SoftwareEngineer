# NekoCafé DevOps PoC

本目录是实验三 D3-2 的源代码与配置仓库，用于展示 NekoCafé 猫咪主题餐饮预约平台从“代码提交”到“容器化运行、镜像扫描、可观测验证、回滚演练”的最小可运行链路。仓库采用 Monorepo 组织方式，将预约服务、会员服务、本地编排、CI/CD 配置、监控配置和运行手册放在同一目录中，便于课程验收时一次性复现实验环境。

## 交付范围

- `services/reservation`：预约服务，使用 Python 标准库实现，提供预约创建、健康检查、Prometheus 指标等能力。
- `services/member`：会员服务，使用 Node.js 标准库实现，提供会员资料、隐私授权、营销退订、健康检查和指标等能力。
- `docker-compose.yml`：本地集成环境，启动 reservation、member、Redis、PostgreSQL、Prometheus 和 Grafana。
- `.github/workflows`：CI/CD 流水线配置，覆盖测试、构建、镜像扫描、部署触发等流程。
- `config/prometheus`：Prometheus 抓取配置，采集两个服务的指标。
- `config/grafana`：Grafana 数据源与 Dashboard 配置，便于查看 RED/USE 指标。
- `docs/runbook.md`：本地运行、验证和排障说明。
- `docs/rollback.md`：发布失败或运行异常时的回滚处理说明。

## 为什么选择 Monorepo

本实验的重点是验证 DevOps 交付闭环，而不是维护一个复杂的多仓库组织。reservation 与 member 两个服务虽然业务边界独立，但它们共享 Compose、CI/CD、镜像扫描、监控采集和课程验收步骤。采用 Monorepo 可以让评审者一次 clone 后直接执行测试、构建、启动和验证命令，降低复现实验的环境成本。

同时，Monorepo 不代表服务没有边界。每个服务仍然拥有独立源码目录、独立 Dockerfile、独立端口、独立健康检查和独立指标。未来如果服务规模扩大，可以按照当前目录边界拆分为独立仓库。

## 前置依赖

- Docker Desktop：用于本地容器编排和镜像构建。
- Docker Compose v2：用于执行 `docker compose up -d --build`。
- Python 3.12 或兼容版本：用于本地运行 reservation 服务测试。
- Node.js 20 或兼容版本：用于本地运行 member 服务测试。
- Trivy：用于本地执行镜像漏洞扫描；也可以通过 Docker 方式运行 Trivy。
- Make：用于使用 `make test`、`make up` 等封装命令。Windows 环境如无法直接使用 Make，可按 Makefile 中的命令逐条执行。

## 本地启动

进入本目录后执行：

```bash
make test
make up
```

如果 Windows PowerShell 中没有 `make`，可改用：

```powershell
python -m unittest discover -s services/reservation/tests -v
npm test --prefix services/member
docker compose up -d --build
```

启动成功后，reservation 对外端口为 `8081`，member 对外端口为 `8082`，Prometheus 为 `9090`，Grafana 为 `3001`。

## 验证步骤

```bash
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
curl http://localhost:8081/metrics
curl http://localhost:8082/metrics
```

预期结果：

- 两个 `/healthz` 端点返回健康状态。
- 两个 `/metrics` 端点返回 Prometheus 文本格式指标。
- 访问 `http://localhost:9090/targets` 时，reservation 与 member 的 target 状态为 `UP`。
- 访问 `http://localhost:3001` 时，可以看到 NekoCafé DevOps Dashboard。Grafana 默认管理员账号为 `admin/admin`，同时已开启匿名只读访问。

## 关键端口

| 组件 | 端口 | 说明 |
| --- | --- | --- |
| reservation | 8081 | 预约服务，对外映射到容器内 8080 |
| member | 8082 | 会员服务，对外映射到容器内 8080 |
| Prometheus | 9090 | 指标采集与查询 |
| Grafana | 3001 | 可视化 Dashboard |
| Redis | 容器内部访问 | 预约锁、缓存和限流能力预留 |
| PostgreSQL | 容器内部访问 | 未来持久化能力预留 |

## 常用命令

```bash
make test      # Python unittest + Node test
make build     # 构建两个服务镜像
make up        # docker compose up -d --build
make down      # docker compose down -v
make logs      # 查看 Compose 服务日志
make scan      # 使用 Trivy 扫描 HIGH/CRITICAL 漏洞
make rollback  # 演示回滚命令
```

## CI/CD 说明

CI 流水线覆盖测试、镜像构建、漏洞扫描和镜像大小统计。任一阶段失败都应阻断合入，避免把无法运行或存在高危漏洞的版本继续交付。CD 流水线用于演示部署触发、环境选择、部署校验和回滚流程，实际 Kubernetes/Helm 细节在 D3-5 中进一步展开。

提交变更前建议按顺序执行：

```bash
make test
make build
make scan
```

如果本地 Trivy 未安装，可以使用 Docker 方式扫描远端镜像：

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 ghcr.io/eridanusq/nekocafe/reservation:0.1.0
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --scanners vuln --severity HIGH,CRITICAL --exit-code 1 ghcr.io/eridanusq/nekocafe/member:0.1.0
```

## Secret 与配置管理

`.env`、token、kubeconfig、数据库密码和第三方平台密钥不提交到仓库。本地演示使用非敏感默认配置；CI/CD 使用 GitHub Secrets；Kubernetes 环境使用 Secret 或环境变量注入。日志中不得直接输出手机号、邮箱、支付凭证、特殊需求备注等敏感信息。

## 停止与清理

```bash
make down
```

该命令会停止并清理 Compose 创建的容器、网络和数据卷。若只想停止容器且保留数据卷，可改用 `docker compose stop`。

## 验收检查清单

- [ ] `make test` 能通过。
- [ ] `make up` 能启动全部服务。
- [ ] `http://localhost:8081/healthz` 正常。
- [ ] `http://localhost:8082/healthz` 正常。
- [ ] Prometheus targets 为 `UP`。
- [ ] Grafana Dashboard 能显示监控面板。
- [ ] Trivy 扫描无 HIGH/CRITICAL 漏洞。
- [ ] runbook 与 rollback 文档能够指导运行、排障和恢复。
