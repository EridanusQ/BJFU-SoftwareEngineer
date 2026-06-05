# NekoCafé Experiment 4 Quality Automation Suite

本目录是 D4-3 自动化测试代码与运行报告，目标是证明 NekoCafé 在功能正确性、服务契约、用户旅程和质量门禁方面具备可运行、可追溯、可复核的自动化证据。目录保留课程模板结构，并补充可直接运行的 Python 目标代码、单元测试、属性测试、契约测试、集成测试、E2E 旅程测试、k6 脚本、ZAP baseline 配置和 HTML 报告生成器。

## 目录说明

- `src/nekocafe_quality/`：课程实验用 PoC 业务代码，覆盖预约创建、取消、手机号脱敏、橘猫语义识别、押金计算和备注转义。
- `unit/`：单元测试，验证纯函数、边界值、异常输入和隐私辅助函数。
- `property/`：属性测试，用确定性样本模拟 PBT，验证手机号脱敏、押金非负、时段收缩、语义稳定和备注安全。
- `contract/`：消费者驱动契约测试，覆盖 `booking-web -> reservation-service`、`member-web -> member-service`、`staff-console -> reservation-service` 三对关系。
- `integration/`：跨模块集成测试，验证预约落库、取消状态、幂等、防污染和异常不落库。
- `e2e/`：三条用户旅程，包括新用户预约取消、老会员推荐下单评价、店员接单调度完单。
- `perf/` 与 `security/`：非功能测试入口，分别对应 k6 压测脚本和 ZAP baseline 配置。
- `reports/`：运行后生成的 HTML、JSON、覆盖率和变异测试报告。

## 本地运行

在 PowerShell 中进入本目录后执行：

```powershell
python .\tools\run_tests.py
python .\tools\mutation_check.py
```

运行完成后查看：

- `reports/index.html`
- `reports/test-results.json`
- `reports/coverage-summary.txt`
- `reports/mutation-summary.md`

## 本次执行结果

- 自动化测试总数：38
- 失败/错误/跳过：0 / 0 / 0
- 行覆盖率：72.5%（79/109）
- 分支覆盖率：70.0%（28/40）
- 变异分数：88.9%（9 个变异样本中杀死 8 个）
- 结论：达到实验四任务书中“行覆盖率 ≥ 70%、分支覆盖率 ≥ 60%、变异分数 ≥ 60%”的门槛。

## 指标口径

- 行覆盖率：由 `trace` 对 `src/nekocafe_quality` 轻量统计，作为课程 PoC 的可复现实验口径。
- 分支覆盖率：按实验四质量门禁中定义的 40 个关键业务分支记录，包括容量校验、时间窗、幂等、语义分类、脱敏、取消状态和备注转义。
- 变异分数：`tools/mutation_check.py` 的 9 个轻量变异样本，覆盖边界比较符、语义误判、脱敏绕过、幂等破坏和 HTML 转义缺失；正式项目可迁移到 `mutmut` 或 `cosmic-ray`。

## CI 迁移建议

本地脚本采用 Python 标准库，便于在课程环境中复现。迁移到实验三流水线时，可将 `python tools/run_tests.py` 作为 PR 门禁，将 `python tools/mutation_check.py` 作为 nightly 或 release 门禁，并在失败时上传 `reports/` 目录作为 Actions artifact。
