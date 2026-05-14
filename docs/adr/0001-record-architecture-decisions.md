# 0001 确立 ADR 制度

Status: Accepted

Context: NekoCafé 架构需要回答服务拆分、数据库、消息、API、鉴权和跨境数据等长期影响问题。若只在报告中给出结论，后续实验和迭代无法知道当时的约束与取舍。

Decision: 项目采用 ADR 记录所有重要架构决策。ADR 从 0001 起递增编号，状态使用 Proposed、Accepted、Deprecated、Superseded。每份 ADR 必须包含 Context、Decision、Consequences、Alternatives Considered、References，并在 Git 仓库 docs/adr/ 中托管。

Consequences: 正面影响是决策可追溯、便于评审和答辩；负面影响是需要额外维护；中性影响是 ADR 不替代 C4、OpenAPI 和代码，只记录为什么这样设计。

Alternatives Considered: 仅在实验报告中描述，被放弃，因为无法按时间演进；只在 Issue 中讨论，被放弃，因为结构不稳定。

References: 实验二任务书；Michael Nygard, Documenting Architecture Decisions.
