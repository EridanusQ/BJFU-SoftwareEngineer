# 0006 采用 OIDC 登录、JWT 访问令牌和 RBAC+ABAC 授权

Status: Accepted

Context: 系统有顾客、店员、猫咪管家、店长、总部运营等角色，还存在门店范围、总部范围、隐私授权和营销授权等属性约束。单纯 RBAC 无法表达 store_id 和 consent 状态。

Decision: 顾客端采用 OIDC/小程序登录换取 JWT，内部服务通过网关校验令牌。授权采用 RBAC+ABAC：RBAC 控制角色能力，ABAC 检查 store_id、member_id、consent_type、operation_scope。关键操作写入审计日志。

Consequences: 正面影响是权限边界明确、支持门店隔离和合规审计；负面影响是策略测试成本上升；中性影响是课程阶段可用简化策略表模拟。

Alternatives Considered: 仅 RBAC 被放弃，因为无法表达门店隔离；Session 单体鉴权被放弃，因为不适合 API 网关和多端。

References: QAS-05；QAS-06；ADR-0005。
