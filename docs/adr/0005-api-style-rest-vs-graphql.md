# 0005 外部与服务间主接口采用 REST，聚合查询由读模型承担

Status: Accepted

Context: 顾客端、店员端和运营端需要稳定 API；实验二要求为预约服务和会员服务提供 OpenAPI 3.0。GraphQL 能减少前端多次请求，但会增加权限、缓存和查询复杂度。

Decision: v1.0 采用 REST + OpenAPI 作为外部和服务间主接口。API 网关负责鉴权、限流、路由和 traceId；复杂运营查询不通过 GraphQL 拼装交易服务，而由运营分析读模型提供专用 REST 端点。

Consequences: 正面影响是契约清晰、易测试、与 Swagger/OpenAPI 工具链一致；负面影响是部分页面可能需要多个端点；中性影响是未来可在 BFF 层引入 GraphQL，但不直接暴露核心服务。

Alternatives Considered: GraphQL 被延后，因为授权和缓存复杂；gRPC 被保留用于未来内部高性能调用，但课程阶段 REST 更利于评审。

References: D2-5 OpenAPI；ADR-0006。
