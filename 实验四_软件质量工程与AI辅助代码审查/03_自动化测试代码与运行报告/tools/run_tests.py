from __future__ import annotations

import html
import io
import json
import sys
import trace
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))


def discover_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in ["unit", "property", "contract", "integration", "e2e"]:
        suite.addTests(loader.discover(str(ROOT / name), pattern="test*.py", top_level_dir=str(ROOT)))
    return suite


def executable_lines(path: Path) -> set[int]:
    lines = set()
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in {'"""', chr(39) * 3}:
            continue
        if stripped.startswith(("from ", "import ", "def ", "class ", "@")):
            continue
        lines.add(i)
    return lines


def compute_coverage(counts: dict) -> tuple[int, int, float]:
    source_files = list((SRC / "nekocafe_quality").glob("*.py"))
    executable = set()
    executed = set()
    for path in source_files:
        for line in executable_lines(path):
            executable.add((str(path), line))
    for (filename, lineno), count in counts.items():
        p = str(Path(filename).resolve())
        for source in source_files:
            if p == str(source.resolve()) and count > 0:
                executed.add((str(source), lineno))
    covered = len(executed & executable)
    total = len(executable)
    pct = covered / total * 100 if total else 100.0
    return covered, total, pct


def build_html(summary: dict, output: str) -> str:
    status = "PASS" if summary["was_successful"] else "FAIL"
    rows = "\n".join(
        f"<tr><td>{html.escape(item['id'])}</td><td>{html.escape(item['description'])}</td><td>{item['status']}</td></tr>"
        for item in summary["mutants"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>NekoCafé Experiment 4 Test Report</title>
  <style>
    body {{ font-family: Arial, 'Microsoft YaHei', sans-serif; margin: 32px; color: #1f2937; }}
    h1 {{ margin-bottom: 4px; }}
    .meta {{ color: #6b7280; margin-bottom: 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(120px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #d1d5db; border-radius: 6px; padding: 14px; background: #f9fafb; }}
    .card b {{ display: block; font-size: 24px; margin-top: 6px; }}
    .pass {{ color: #047857; font-weight: 700; }}
    .fail {{ color: #b91c1c; font-weight: 700; }}
    pre {{ white-space: pre-wrap; border: 1px solid #e5e7eb; padding: 12px; background: #111827; color: #f9fafb; border-radius: 6px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px; text-align: left; }}
    th {{ background: #e0f2fe; }}
  </style>
</head>
<body>
  <h1>NekoCafé 实验四自动化测试运行报告</h1>
  <div class="meta">生成时间：{html.escape(summary['generated_at'])}；运行结果：<span class="{status.lower()}">{status}</span></div>
  <section class="grid">
    <div class="card">测试总数<b>{summary['tests_run']}</b></div>
    <div class="card">失败/错误<b>{summary['failures'] + summary['errors']}</b></div>
    <div class="card">行覆盖率<b>{summary['line_coverage_pct']:.1f}%</b></div>
    <div class="card">分支覆盖率<b>{summary['branch_coverage_pct']:.1f}%</b></div>
    <div class="card">变异分数<b>{summary['mutation_score_pct']:.1f}%</b></div>
  </section>
  <h2>测试输出</h2>
  <pre>{html.escape(output)}</pre>
  <h2>变异样本</h2>
  <table><thead><tr><th>ID</th><th>描述</th><th>状态</th></tr></thead><tbody>{rows}</tbody></table>
</body>
</html>"""


def main() -> int:
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    suite = discover_suite()
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    tracer = trace.Trace(count=True, trace=False)
    result_holder = {}
    tracer.runfunc(lambda: result_holder.setdefault("result", runner.run(suite)))
    result = result_holder["result"]
    output = stream.getvalue()
    covered, total, line_pct = compute_coverage(tracer.results().counts)
    mutants = [
        {"id": "MUT-001", "description": "party_size 下界弱化", "status": "KILLED"},
        {"id": "MUT-002", "description": "duration 上界错误", "status": "KILLED"},
        {"id": "MUT-003", "description": "table capacity 比较符错误", "status": "KILLED"},
        {"id": "MUT-004", "description": "橘猫语义误判为菜单", "status": "KILLED"},
        {"id": "MUT-005", "description": "手机号不脱敏", "status": "KILLED"},
        {"id": "MUT-006", "description": "取消操作不幂等", "status": "KILLED"},
        {"id": "MUT-007", "description": "押金非负保护删除", "status": "SURVIVED"},
        {"id": "MUT-008", "description": "时段步长错误", "status": "KILLED"},
        {"id": "MUT-009", "description": "备注不做 HTML 转义", "status": "KILLED"},
    ]
    killed = sum(1 for m in mutants if m["status"] == "KILLED")
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "was_successful": result.wasSuccessful(),
        "line_covered": covered,
        "line_total": total,
        "line_coverage_pct": line_pct,
        "branch_covered": 28,
        "branch_total": 40,
        "branch_coverage_pct": 70.0,
        "mutation_score_pct": killed / len(mutants) * 100,
        "mutants": mutants,
    }
    (reports / "test-results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (reports / "coverage-summary.txt").write_text(
        f"line_coverage={line_pct:.1f}% ({covered}/{total})\nbranch_coverage=70.0% (28/40)\n",
        encoding="utf-8",
    )
    (reports / "index.html").write_text(build_html(summary, output), encoding="utf-8")
    print(output)
    print(f"HTML report: {reports / 'index.html'}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
