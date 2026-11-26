#!/usr/bin/env python3
"""Generate a deterministic daily report as Markdown.

Pure-stdlib, no third-party dependencies. The report content depends only on
the given date, so repeated runs on the same day produce identical output.
"""

import argparse
import sys
from datetime import date, datetime, timedelta, timezone

WEEKDAY_CN = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

TIPS = [
    "把大任务拆成能在 30 分钟内完成的小步骤。",
    "写完代码先跑一遍自检，再交给别人看。",
    "每天留 10 分钟回顾今天学到的一个知识点。",
    "重要的结论要配上可复现的验证命令。",
    "先让流程跑通，再优化细节。",
    "遇到反复失败时，先缩小问题范围再下手。",
    "把常用命令记下来，下次直接复用。",
]


def select_tip(day: date) -> str:
    """Pick a tip deterministically from the day's ordinal number."""
    return TIPS[day.toordinal() % len(TIPS)]


def iso_week(day: date) -> int:
    """ISO week number of the given date."""
    return day.isocalendar()[1]


def build_report(day: date, generated_at: datetime) -> str:
    """Build the full Markdown report text from a date and a timestamp."""
    lines = [
        f"# 每日报告 {day.isoformat()}",
        "",
        f"- 日期：{day.isoformat()}（{WEEKDAY_CN[day.weekday()]}）",
        f"- ISO 周：第 {iso_week(day)} 周",
        f"- 生成时间（UTC）：{generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 今日提示",
        "",
        select_tip(day),
        "",
        "## 说明",
        "",
        "本报告由 GitHub Actions 定时任务自动生成并提交，内容由脚本确定性生成。",
        "",
    ]
    return "\n".join(lines)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def self_test() -> int:
    """Deterministic checks; returns 0 on success, 1 on failure."""
    d1 = date(2026, 11, 26)
    d2 = date(2026, 11, 26)
    d3 = date(2026, 11, 27)
    ts1 = datetime(2026, 11, 26, 0, 0, tzinfo=timezone.utc)
    ts2 = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)

    checks = [
        ("同名日期生成相同提示", select_tip(d1) == select_tip(d2)),
        ("不同日期提示取自同一列表", select_tip(d1) in TIPS and select_tip(d3) in TIPS),
        ("同一日期正文确定（忽略时间戳行）",
         "\n".join(l for l in build_report(d1, ts1).splitlines() if "生成时间" not in l)
         == "\n".join(l for l in build_report(d1, ts2).splitlines() if "生成时间" not in l)),
        ("ISO 周在合理范围", 1 <= iso_week(d1) <= 53),
        ("中文星期正确", WEEKDAY_CN[d1.weekday()] == "星期四"),
    ]
    ok = True
    for name, passed in checks:
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
        if not passed:
            ok = False
    return 0 if ok else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate a daily Markdown report.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD (default: today in UTC)")
    parser.add_argument("--output", help="Output .md path (default: stdout)")
    parser.add_argument("--self-test", action="store_true", help="Run deterministic self-checks")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    day = parse_date(args.date) if args.date else datetime.now(timezone.utc).date()
    generated_at = datetime.now(timezone.utc)
    text = build_report(day, generated_at)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"Wrote {args.output} for {day.isoformat()}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
