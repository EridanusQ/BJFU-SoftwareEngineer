# NekoCafé ADR Index

- [0001-record-architecture-decisions: 确立 ADR 制度](./0001-record-architecture-decisions.md)
- [0002-microservice-granularity: 按限界上下文确定微服务粒度](./0002-microservice-granularity.md)
- [0003-database-selection: 核心交易采用 PostgreSQL，读模型按需扩展](./0003-database-selection.md)
- [0004-message-broker-selection: 采用 Kafka 风格事件流，课程实现可用轻量队列替代](./0004-message-broker-selection.md)
- [0005-api-style-rest-vs-graphql: 外部与服务间主接口采用 REST，聚合查询由读模型承担](./0005-api-style-rest-vs-graphql.md)
- [0006-authn-and-authz: 采用 OIDC 登录、JWT 访问令牌和 RBAC+ABAC 授权](./0006-authn-and-authz.md)
- [0007-cross-border-data-strategy: 默认数据本地化，跨境仅传脱敏聚合特征](./0007-cross-border-data-strategy.md)
