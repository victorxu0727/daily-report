# 每日自动报告（GitHub Actions 示例）

一套可直接运行的自动化：每天定时生成一份 Markdown 报告并提交回本仓库，同时附带代码检查流水线。

## 自动化内容

1. **每日自动报告**（`.github/workflows/daily-report.yml`）
   - 触发：`schedule` 每天 UTC 02:00（北京时间 10:00），也支持在 Actions 页面手动触发。
   - 动作：运行 `scripts/generate_report.py` 生成 `reports/YYYY-MM-DD.md`，检测到变更才提交并推送，避免空提交。
   - 权限：`contents: write`（仅仓库内容写权限，作用域最小化）。

2. **代码检查**（`.github/workflows/ci.yml`）
   - 触发：`scripts/` 或 workflow 文件发生 push / PR 时，也支持手动触发。
   - 动作：Python 语法检查 + 生成脚本的确定性自检。

## 生成脚本

`scripts/generate_report.py` 仅用 Python 标准库，无第三方依赖。

- 报告内容只由日期决定（同一天重复运行正文一致），便于验证。
- `--date YYYY-MM-DD` 指定日期，`--output 路径` 写文件（默认输出到终端）。
- `--self-test` 运行确定性检查，CI 里会执行。

本地试跑：

```bash
python scripts/generate_report.py
python scripts/generate_report.py --date 2026-11-26 --output reports/2026-11-26.md
python scripts/generate_report.py --self-test
```

## 时区说明

GitHub Actions 的 `cron` 一律按 UTC 计算。本仓库用 UTC 02:00 对应北京时间 10:00。
