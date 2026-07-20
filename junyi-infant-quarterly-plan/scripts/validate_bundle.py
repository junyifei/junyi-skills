#!/usr/bin/env python3
"""Validate the public 0-35 month quarterly plan input bundle."""

from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


INTAKE_SCHEMA = "junyi-child-growth-intake/v1"
UPDATE_SCHEMA = "junyi-child-quarterly-update/v1"
ANNUAL_TITLE = "# 0—3 岁全年成长规划"
ANNUAL_BOUNDARY = "本规划不替代医疗、心理、发育筛查或教育专业评估"
UPDATE_HEADINGS = (
    "## 1. 季度变化与执行复盘",
    "## 2. 证据与来源",
    "## 3. 资料完整性与未知",
    "## 4. 月龄路由与交接结果",
)
EVENT_BLOCK_RE = re.compile(
    r"(?ms)^### Q\d+\s*$\n(.*?)(?=^### Q\d+\s*$|^##\s+|\Z)"
)
FIELD_RE_TEMPLATE = r"^- {label}：\s*(.+?)\s*$"
EMPTY_FACTS = {"", "（空）", "(空)", "空", "unknown", "none", "n/a", "na", "待补充", "未提供", "无具体事件"}
SENSITIVE = (
    re.compile(r"/" r"Users/[^\s)]+"),
    re.compile(r"(?i)\b(?:app_secret|access_token|refresh_token|api_key)\b\s*[:=]"),
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("quarterly update 缺少 YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("quarterly update frontmatter 未闭合") from exc
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line or line.startswith((" ", "\t")):
            raise ValueError(f"无效 frontmatter 行：{line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data, "\n".join(lines[end + 1 :])


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def complete_months(birth: date, as_of: date) -> int:
    months = (as_of.year - birth.year) * 12 + as_of.month - birth.month
    anniversary_day = min(birth.day, calendar.monthrange(as_of.year, as_of.month)[1])
    return months - (as_of.day < anniversary_day)


def event_blocks(body: str) -> list[str]:
    return [match.group(1) for match in EVENT_BLOCK_RE.finditer(body)]


def field_value(block: str, label: str) -> str | None:
    pattern = re.compile(FIELD_RE_TEMPLATE.format(label=re.escape(label)), re.MULTILINE)
    match = pattern.search(block)
    if not match:
        return None
    value = match.group(1).strip()
    return value if value.lower() not in EMPTY_FACTS else None


def validate(intake: Any, update_text: str, annual_text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(intake, dict):
        return ["intake 根节点必须是 JSON 对象"], warnings
    if intake.get("schema_version") != INTAKE_SCHEMA:
        errors.append(f"intake.schema_version 必须是 {INTAKE_SCHEMA}")
    try:
        update, body = parse_frontmatter(update_text)
    except ValueError as exc:
        return [str(exc)], warnings

    if update.get("schema_version") != UPDATE_SCHEMA:
        errors.append(f"update.schema_version 必须是 {UPDATE_SCHEMA}")
    if update.get("status") != "ready":
        errors.append("季度资料必须为 status: ready；其他状态不能生成正式计划")
    if update.get("plan_track") != "infant":
        errors.append("本 Skill 只接受 plan_track: infant")
    if update.get("child_voice_status") not in {"behavioral", "direct"}:
        errors.append("0—35 月龄需要 behavioral 或 direct 孩子信号")
    for heading in UPDATE_HEADINGS:
        if heading not in body:
            errors.append(f"quarterly update 缺少章节：{heading}")

    child = intake.get("child") if isinstance(intake.get("child"), dict) else {}
    if update.get("child_id") != child.get("id"):
        errors.append("update.child_id 必须与 intake.child.id 一致")
    birth = parse_date(child.get("birth_date"))
    start = parse_date(update.get("quarter_start"))
    try:
        declared_age = int(update.get("age_months", ""))
        evidence_count = int(update.get("evidence_count", ""))
        context_count = int(update.get("context_count", ""))
    except ValueError:
        declared_age = evidence_count = context_count = -1
        errors.append("age_months、evidence_count 和 context_count 必须是整数")
    if birth is None or start is None:
        errors.append("出生日期和 quarter_start 必须是有效日期")
    else:
        calculated_age = complete_months(birth, start)
        if calculated_age != declared_age:
            errors.append(f"季度开始月龄应为 {calculated_age}，不是 {declared_age}")
        if not 0 <= calculated_age <= 35:
            errors.append(f"季度开始月龄 {calculated_age} 不属于 0—35 月龄")
    if evidence_count < 3:
        errors.append("正式季度计划至少需要 3 个本季度具体事件")
    if context_count < 2:
        errors.append("正式季度计划至少需要 2 个生活情境")
    blocks = event_blocks(body)
    body_contexts = {value for block in blocks if (value := field_value(block, "场景"))}
    if len(blocks) != evidence_count:
        errors.append(f"正文 Qxx 数量为 {len(blocks)}，与 evidence_count={evidence_count} 不一致")
    if len(body_contexts) != context_count:
        errors.append(f"正文生活情境数量为 {len(body_contexts)}，与 context_count={context_count} 不一致")
    for index, block in enumerate(blocks, 1):
        if not field_value(block, "事实或原话"):
            errors.append(f"Q{index} 缺少非空事实或原话")
        if not field_value(block, "来源"):
            errors.append(f"Q{index} 缺少已知来源")

    if ANNUAL_TITLE not in annual_text:
        errors.append("annual plan 不是完整的 0—3 岁全年规划")
    if ANNUAL_BOUNDARY not in annual_text:
        errors.append("annual plan 缺少专业边界声明")
    if any(pattern.search(update_text) for pattern in SENSITIVE):
        errors.append("quarterly update 包含私有路径或疑似凭证")
    if intake.get("plan_track") != "infant":
        warnings.append("全年 intake 来自旧年龄轨道；仅在季度资料已明确轨道过渡时作为历史底座使用")
    return sorted(set(errors)), sorted(set(warnings))


def sample() -> tuple[dict[str, Any], str, str]:
    intake = {
        "schema_version": INTAKE_SCHEMA,
        "plan_track": "infant",
        "child": {"id": "CHILD-A", "birth_date": "2024-06-15"},
    }
    update = """---
schema_version: junyi-child-quarterly-update/v1
status: ready
plan_track: infant
quarter_start: 2026-07-01
quarter_end: 2026-09-30
as_of: 2026-06-20
child_id: CHILD-A
age_months: 24
annual_plan_as_of: 2026-01-15
previous_plan_status: provided
child_voice_status: behavioral
track_transition: false
evidence_count: 3
context_count: 2
---
## 1. 季度变化与执行复盘
## 2. 证据与来源
### Q1
- 场景：家庭游戏
- 事实或原话：孩子主动继续搭建
- 来源：家长
### Q2
- 场景：户外活动
- 事实或原话：孩子主动靠近并重复探索
- 来源：家长
### Q3
- 场景：家庭游戏
- 事实或原话：孩子用动作表达停止
- 来源：家长
## 3. 资料完整性与未知
## 4. 月龄路由与交接结果
"""
    annual = f"{ANNUAL_TITLE}\n\n{ANNUAL_BOUNDARY}"
    return intake, update, annual


def self_test() -> int:
    intake, update, annual = sample()
    if validate(intake, update, annual)[0]:
        print("SELF-TEST FAIL: valid bundle rejected", file=sys.stderr)
        return 1
    broken = update.replace("status: ready", "status: needs-observation")
    if not validate(intake, broken, annual)[0]:
        print("SELF-TEST FAIL: non-ready bundle accepted", file=sys.stderr)
        return 1
    print("SELF-TEST PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path)
    parser.add_argument("--update", type=Path)
    parser.add_argument("--annual-plan", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not all((args.intake, args.update, args.annual_plan)):
        parser.error("--intake, --update and --annual-plan are required")
    try:
        intake = json.loads(args.intake.read_text(encoding="utf-8"))
        update = args.update.read_text(encoding="utf-8")
        annual = args.annual_plan.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(intake, update, annual)
    print("PASS" if not errors else "FAIL")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
