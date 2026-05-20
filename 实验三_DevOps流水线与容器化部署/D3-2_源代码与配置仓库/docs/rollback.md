# Rollback Plan

## Helm 回滚

```bash
helm history nekocafe -n nekocafe-staging
helm rollback nekocafe <REVISION> -n nekocafe-staging
kubectl rollout status deploy/nekocafe-reservation -n nekocafe-staging
```

## 触发条件

- 5 分钟窗口 P95 延迟 > 350ms。
- 5 分钟窗口错误率 > 1%。
- readiness 探针连续失败。

## 数据兼容

只允许向后兼容迁移；破坏性 schema 变更必须拆成 expand -> migrate -> contract 三步。
