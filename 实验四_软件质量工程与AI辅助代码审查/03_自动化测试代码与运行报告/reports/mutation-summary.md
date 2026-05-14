# 轻量变异检查报告

变异样本数：9
杀死变异：8
变异分数：88.9%

| ID | 变异描述 | 状态 |
| --- | --- | --- |
| MUT-001 | party_size < 1 改为 party_size < 0 | KILLED |
| MUT-002 | duration > 180 改为 duration >= 180 | KILLED |
| MUT-003 | table_capacity < party 改为 <= | KILLED |
| MUT-004 | 橘猫分类改为 menu 优先 | KILLED |
| MUT-005 | mask_phone 不隐藏中间四位 | KILLED |
| MUT-006 | cancel idempotent 改为异常 | KILLED |
| MUT-007 | quote_deposit 去掉非负保护 | SURVIVED |
| MUT-008 | available_slots 步长改为 60 分钟 | KILLED |
| MUT-009 | sanitize_note 不做 html.escape | KILLED |
