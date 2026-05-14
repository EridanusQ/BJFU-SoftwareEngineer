# NekoCafé Experiment 4 Quality Automation Suite

本目录是 D4-3 自动化测试代码与运行报告。它保留课程模板目录结构，并补充可直接运行的 Python 目标代码、单元测试、属性测试、契约测试、集成测试、E2E 旅程测试、k6 脚本、ZAP baseline 配置和 HTML 报告生成器。

## 本地运行

```powershell
python tools/run_tests.py
```

运行完成后查看：

- `reports/index.html`
- `reports/test-results.json`
- `reports/coverage-summary.txt`
- `reports/mutation-summary.md`

## 指标口径

- 行覆盖率：由 `trace` 对 `src/nekocafe_quality` 轻量统计。
- 分支覆盖率：按实验四质量门禁中定义的 40 个关键业务分支记录。
- 变异分数：`tools/mutation_check.py` 的 9 个轻量变异样本，作为课程 PoC 证据；正式项目可迁移到 mutmut/cosmic-ray。
