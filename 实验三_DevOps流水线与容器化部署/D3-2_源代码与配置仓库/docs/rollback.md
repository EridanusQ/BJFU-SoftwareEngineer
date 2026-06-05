# NekoCafé Rollback Plan

本回滚手册用于说明实验三发布失败或运行指标异常时的恢复路径。PoC 阶段以 Helm 回滚和 Compose 本地恢复为主，生产态可进一步接入自动化灰度和告警审批。

## 1. 回滚触发条件

满足以下任一情况时，应暂停发布并考虑回滚：

- 5 分钟窗口内 P95 延迟大于 `350ms`。
- 5 分钟窗口内错误率大于 `1%`。
- readiness 或 liveness 探针连续失败。
- Pod 重启次数异常增长。
- 新版本发布后关键业务接口不可用。
- Trivy 或其他安全扫描发现 HIGH/CRITICAL 漏洞且无法立即修复。

## 2. Helm 回滚流程

先查看历史版本：

```bash
helm history nekocafe -n nekocafe-staging
```

选择上一稳定版本后执行：

```bash
helm rollback nekocafe <REVISION> -n nekocafe-staging
kubectl rollout status deploy/nekocafe-reservation -n nekocafe-staging
kubectl rollout status deploy/nekocafe-member -n nekocafe-staging
```

回滚完成后检查服务健康：

```bash
kubectl get pods -n nekocafe-staging
kubectl get svc -n nekocafe-staging
kubectl logs deploy/nekocafe-reservation -n nekocafe-staging --tail=100
kubectl logs deploy/nekocafe-member -n nekocafe-staging --tail=100
```

## 3. 本地 Compose 恢复

如果本地演示环境异常，可先停止并清理当前环境：

```bash
make down
```

重新构建并启动：

```bash
make up
```

如怀疑镜像构建缓存导致异常，可清理对应镜像后重新构建：

```bash
docker image rm nekocafe/reservation:0.1.0
docker image rm nekocafe/member:0.1.0
make up
```

## 4. 数据兼容原则

数据库变更必须遵循向后兼容原则。禁止将破坏性 schema 变更和应用发布绑定在同一次操作中。推荐采用：

1. expand：先新增字段、索引或表结构，保持旧版本仍可运行。
2. migrate：迁移数据并验证读写结果。
3. contract：确认旧版本不再使用后，再移除旧字段或旧逻辑。

PoC 阶段主要展示规则与流程，实际生产环境需要额外准备备份、恢复演练和数据一致性校验。

## 5. 回滚后验证

回滚不是结束，还需要确认系统恢复到稳定状态：

- `/healthz` 正常。
- Prometheus targets 为 `UP`。
- Grafana 中错误率下降，延迟恢复到阈值以内。
- 关键业务接口可访问。
- 回滚版本、触发原因、处理人和恢复时间已记录。

## 6. 复盘记录

每次回滚后至少记录以下内容：

- 触发时间与影响范围。
- 异常指标或失败日志。
- 回滚到的版本号或 Helm Revision。
- 根因分析结论。
- 后续预防措施，例如新增测试、调整阈值、补充告警或完善 runbook。
