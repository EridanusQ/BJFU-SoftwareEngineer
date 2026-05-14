# 0004 采用 Kafka 风格事件流，课程实现可用轻量队列替代

Status: Accepted

Context: 预约、订单、会员、猫咪健康和活动投放事件需要驱动通知、运营看板和推荐更新。系统需要事件可重放、顺序消费和较高吞吐，但课程实验阶段不一定部署完整 Kafka 集群。

Decision: 目标架构采用 Kafka 作为事件流平台，关键主题包括 reservation-events、order-events、member-events、cat-health-events、campaign-events。每个写服务采用 Outbox Pattern 先写本地事务再投递事件；课程 PoC 可用 RabbitMQ 或内存队列模拟，但 ADR 目标态以 Kafka 为准。

Consequences: 正面影响是读模型可重建、服务解耦、可支撑运营看板；负面影响是运维成本和消息语义复杂；中性影响是核心同步调用仍保留在预约创建等低延迟链路。

Alternatives Considered: RabbitMQ 更易上手但重放和大吞吐较弱；RocketMQ 适合国内生态但课程资料和团队熟悉度较低；仅 REST 同步调用被放弃，因为会放大耦合。

References: QAS-07；D2-4 L2 容器图；ADR-0002。
