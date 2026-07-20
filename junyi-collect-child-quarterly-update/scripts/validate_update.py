#!/usr/bin/env python3
"""Validate a junyi child quarterly-update Markdown file with stdlib only."""

from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date
from pathlib import Path


SCHEMA_VERSION = "junyi-child-quarterly-update/v1"
STATUSES = {"ready", "needs-observation", "blocked-safety", "blocked-upstream"}
TRACKS = {"infant", "preschool", "school-age"}
PREVIOUS_STATUSES = {"provided", "first-cycle", "unavailable"}
VOICE_STATUSES = {
    "behavioral",
    "direct",
    "direct-simple",
    "direct-reflection",
    "unavailable",
}
REQUIRED_HEADINGS = (
    "## 1. 季度变化与执行复盘",
    "## 2. 证据与来源",
    "## 3. 资料完整性与未知",
    "## 4. 月龄路由与交接结果",
)
EVENT_HEADING_RE = re.compile(r"^### Q\d+$", re.MULTILINE)
EVENT_BLOCK_RE = re.compile(
    r"(?ms)^### Q\d+\s*$\n(.*?)(?=^### Q\d+\s*$|^##\s+|\Z)"
)
FIELD_RE_TEMPLATE = r"^- {label}：\s*(.+?)\s*$"
SENSITIVE = (
    re.compile(r"/" r"Users/[^\s)]+"),
    re.compile(
        r"(?i)\b(?:app[_-]?secret|access[_-]?token|refresh[_-]?token|api[_-]?key|password)\b\s*[:=]"
    ),
)
EMPTY_FACTS = {
    "",
    "（空）",
    "(空)",
    "空",
    "unknown",
    "none",
    "n/a",
    "na",
    "待补充",
    "未提供",
    "无具体事件",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("update", nargs="?", type=Path, help="Path to quarterly-update.md")
    parser.add_argument("--intake", type=Path, help="Optional annual intake JSON")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Fail unless the update is ready for a formal quarterly report",
    )
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing YAML frontmatter delimiter") from exc

    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data, "\n".join(lines[end + 1 :])


def parse_date(value: str, field: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field} must use YYYY-MM-DD: {value!r}")
        return None


def complete_months(birth: date, as_of: date) -> int:
    months = (as_of.year - birth.year) * 12 + as_of.month - birth.month
    if as_of.day < min(birth.day, calendar.monthrange(as_of.year, as_of.month)[1]):
        months -= 1
    return months


def track_for_months(months: int) -> str | None:
    if 0 <= months <= 35:
        return "infant"
    if 36 <= months <= 71:
        return "preschool"
    if 72 <= months <= 144:
        return "school-age"
    return None


def values_for_label(body: str, label: str) -> list[str]:
    pattern = re.compile(FIELD_RE_TEMPLATE.format(label=re.escape(label)), re.MULTILINE)
    return [value.strip() for value in pattern.findall(body)]


def event_blocks(body: str) -> list[str]:
    return [match.group(1) for match in EVENT_BLOCK_RE.finditer(body)]


def usable_value(block: str, label: str) -> str | None:
    values = values_for_label(block, label)
    if not values:
        return None
    value = values[0].strip()
    return value if value.lower() not in EMPTY_FACTS else None


def validate_voice(track: str, age_months: int, voice: str, errors: list[str]) -> None:
    if track == "infant" and voice not in {"behavioral", "direct"}:
        errors.append("ready infant update requires behavioral or direct child voice")
    elif track == "preschool" and voice not in {"direct-simple", "direct-reflection"}:
        errors.append("ready preschool update requires direct child expression")
    elif track == "school-age":
        if 72 <= age_months <= 107 and voice not in {"direct-simple", "direct-reflection"}:
            errors.append("ready age 6-8 update requires at least direct-simple child voice")
        elif 108 <= age_months <= 144 and voice != "direct-reflection":
            errors.append("ready age 9-12 update requires direct-reflection child voice")


def validate_document(
    text: str,
    *,
    intake: dict[str, object] | None = None,
    require_ready: bool = False,
) -> list[str]:
    errors: list[str] = []
    try:
        meta, body = parse_frontmatter(text)
    except ValueError as exc:
        return [str(exc)]

    required_meta = {
        "schema_version",
        "status",
        "plan_track",
        "quarter_start",
        "quarter_end",
        "as_of",
        "child_id",
        "age_months",
        "annual_plan_as_of",
        "previous_plan_status",
        "child_voice_status",
        "track_transition",
        "evidence_count",
        "context_count",
    }
    missing = sorted(required_meta - set(meta))
    if missing:
        errors.append(f"missing frontmatter fields: {', '.join(missing)}")

    if meta.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    status = meta.get("status", "")
    track = meta.get("plan_track", "")
    voice = meta.get("child_voice_status", "")
    if status not in STATUSES:
        errors.append(f"invalid status: {status!r}")
    if track not in TRACKS:
        errors.append(f"invalid plan_track: {track!r}")
    if meta.get("previous_plan_status") not in PREVIOUS_STATUSES:
        errors.append("invalid previous_plan_status")
    if voice not in VOICE_STATUSES:
        errors.append(f"invalid child_voice_status: {voice!r}")
    if meta.get("track_transition") not in {"true", "false"}:
        errors.append("track_transition must be true or false")
    if require_ready and status != "ready":
        errors.append(f"formal report handoff requires status ready, got {status!r}")

    start = parse_date(meta.get("quarter_start", ""), "quarter_start", errors)
    end = parse_date(meta.get("quarter_end", ""), "quarter_end", errors)
    parse_date(meta.get("as_of", ""), "as_of", errors)
    if start and end and end < start:
        errors.append("quarter_end must not be earlier than quarter_start")

    try:
        age_months = int(meta.get("age_months", ""))
        evidence_count = int(meta.get("evidence_count", ""))
        context_count = int(meta.get("context_count", ""))
    except ValueError:
        age_months = evidence_count = context_count = -1
        errors.append("age_months, evidence_count and context_count must be integers")

    calculated_track = track_for_months(age_months)
    if calculated_track != track:
        errors.append(
            f"age_months {age_months} maps to {calculated_track!r}, not {track!r}"
        )

    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"missing heading: {heading}")
    if status == "needs-observation" and "## 7—14 天预备观察方案" not in body:
        errors.append("needs-observation status requires a 7—14 day observation plan")

    blocks = event_blocks(body)
    event_count = len(blocks)
    if event_count != evidence_count:
        errors.append(
            f"evidence_count says {evidence_count}, but found {event_count} Qxx event headings"
        )
    contexts = {value for block in blocks if (value := usable_value(block, "场景"))}
    if len(contexts) != context_count:
        errors.append(
            f"context_count says {context_count}, but found {len(contexts)} unique event contexts"
        )

    if status == "ready":
        if evidence_count < 3:
            errors.append("ready update requires at least 3 evidence events")
        if context_count < 2:
            errors.append("ready update requires at least 2 distinct contexts")
        if meta.get("annual_plan_as_of") == "unknown":
            errors.append("ready update requires a known annual_plan_as_of date")
        else:
            parse_date(meta.get("annual_plan_as_of", ""), "annual_plan_as_of", errors)
        if track in TRACKS and age_months >= 0:
            validate_voice(track, age_months, voice, errors)
        for index, block in enumerate(blocks, 1):
            if not usable_value(block, "事实或原话"):
                errors.append(f"ready event Q{index} requires a non-empty 事实或原话")
            if not usable_value(block, "来源"):
                errors.append(f"ready event Q{index} requires a known 来源")

    if any(pattern.search(text) for pattern in SENSITIVE):
        errors.append("quarterly update contains a private path or possible credential")

    if intake is not None:
        child = intake.get("child")
        if not isinstance(child, dict):
            errors.append("intake.child must be an object")
        else:
            intake_id = str(child.get("id", ""))
            if intake_id and meta.get("child_id") != intake_id:
                errors.append("child_id does not match intake child.id")
            birth_raw = child.get("birth_date")
            if start and isinstance(birth_raw, str):
                try:
                    birth = date.fromisoformat(birth_raw)
                except ValueError:
                    errors.append("intake child.birth_date must use YYYY-MM-DD")
                else:
                    calculated_age = complete_months(birth, start)
                    if calculated_age != age_months:
                        errors.append(
                            f"age_months is {age_months}, calculated {calculated_age} from intake"
                        )
                    intake_track = track_for_months(calculated_age)
                    if intake_track != track:
                        errors.append(
                            f"quarter start maps to {intake_track!r}, not plan_track {track!r}"
                        )

    return errors


def self_test() -> int:
    ready = """---
schema_version: junyi-child-quarterly-update/v1
status: ready
plan_track: preschool
quarter_start: 2026-07-01
quarter_end: 2026-09-30
as_of: 2026-06-28
child_id: CHILD-001
age_months: 52
annual_plan_as_of: 2026-01-15
previous_plan_status: provided
child_voice_status: direct-simple
track_transition: false
evidence_count: 3
context_count: 2
---
## 1. 季度变化与执行复盘
## 2. 证据与来源
### Q01
- 场景：家庭游戏
- 事实或原话：孩子主动延续搭建并说想继续
- 来源：孩子和家长
### Q02
- 场景：幼儿园
- 事实或原话：孩子向教师表达不想突然结束游戏
- 来源：孩子和教师
### Q03
- 场景：家庭游戏
- 事实或原话：孩子在预告后完成收尾
- 来源：家长
## 3. 资料完整性与未知
## 4. 月龄路由与交接结果
"""
    errors = validate_document(ready, require_ready=True)
    if errors:
        print("self-test ready case failed:", *errors, sep="\n- ", file=sys.stderr)
        return 1

    broken = ready.replace("child_voice_status: direct-simple", "child_voice_status: unavailable")
    if not validate_document(broken, require_ready=True):
        print("self-test broken voice case was not rejected", file=sys.stderr)
        return 1
    print("self-test PASS")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return self_test()
    if args.update is None:
        print("update file is required unless --self-test is used", file=sys.stderr)
        return 2
    if not args.update.is_file():
        print(f"update file not found: {args.update}", file=sys.stderr)
        return 2
    intake: dict[str, object] | None = None
    if args.intake:
        try:
            intake = json.loads(args.intake.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"cannot read intake JSON: {exc}", file=sys.stderr)
            return 2
    errors = validate_document(
        args.update.read_text(encoding="utf-8"),
        intake=intake,
        require_ready=args.require_ready,
    )
    if errors:
        print("quarterly update validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("quarterly update validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
