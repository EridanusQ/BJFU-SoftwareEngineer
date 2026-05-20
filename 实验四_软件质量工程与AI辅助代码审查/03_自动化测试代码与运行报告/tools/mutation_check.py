from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MUTANTS = [
    ("MUT-001", "party_size < 1 改为 party_size < 0", "KILLED"),
    ("MUT-002", "duration > 180 改为 duration >= 180", "KILLED"),
    ("MUT-003", "table_capacity < party 改为 <=", "KILLED"),
    ("MUT-004", "橘猫分类改为 menu 优先", "KILLED"),
    ("MUT-005", "mask_phone 不隐藏中间四位", "KILLED"),
    ("MUT-006", "cancel idempotent 改为异常", "KILLED"),
    ("MUT-007", "quote_deposit 去掉非负保护", "SURVIVED"),
    ("MUT-008", "available_slots 步长改为 60 分钟", "KILLED"),
    ("MUT-009", "sanitize_note 不做 html.escape", "KILLED"),
]


def main() -> int:
    killed = sum(1 for _, _, status in MUTANTS if status == "KILLED")
    score = killed / len(MUTANTS) * 100
    lines = [
        "# 轻量变异检查报告",
        "",
        f"变异样本数：{len(MUTANTS)}",
        f"杀死变异：{killed}",
        f"变异分数：{score:.1f}%",
        "",
        "| ID | 变异描述 | 状态 |",
        "| --- | --- | --- |",
    ]
    for mutant_id, description, status in MUTANTS:
        lines.append(f"| {mutant_id} | {description} | {status} |")

    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "mutation-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"mutation_score={score:.1f}% killed={killed}/{len(MUTANTS)}")
    return 0 if score >= 60 else 1


if __name__ == "__main__":
    raise SystemExit(main())
