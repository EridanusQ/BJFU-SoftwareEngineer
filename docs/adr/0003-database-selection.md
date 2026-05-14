# 0003 核心交易采用 PostgreSQL，读模型按需扩展

Status: Accepted

Context: 预约、订单、支付、会员授权等数据具有明确关系、事务边界和审计要求。运营看板需要聚合查询，猫咪档案和推荐特征可接受较松散结构。

Decision: 核心写模型采用 PostgreSQL，执行 Database per Service，每个服务拥有自己的 schema 或数据库账号；预约、订单、支付使用关系模型和唯一约束保障并发；运营分析读模型可使用 PostgreSQL 汇总表，后续按规模演进到 ClickHouse/Elasticsearch。

Consequences: 正面影响是事务、索引、约束和审计能力强；负面影响是跨服务查询不能直接 join，需要事件同步；中性影响是开发阶段可共用数据库实例但不能共享表所有权。

Alternatives Considered: MongoDB 被放弃作为核心库，因为预约并发和支付对账更适合关系约束；图数据库被放弃，因为当前没有复杂关系遍历主场景。

References: D2-6 数据字典；QAS-04；ADR-0002。
