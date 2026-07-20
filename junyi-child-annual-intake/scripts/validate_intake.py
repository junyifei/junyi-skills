#!/usr/bin/env python3
"""Validate the public child-growth intake contract and age routing."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

SCHEMA = "junyi-child-growth-intake/v1"
TRACKS = {"infant": (0, 36), "preschool": (36, 72), "school-age": (72, 145)}
REQUIRED_SECTIONS = {"context", "goals", "strengths", "routines", "observations", "multiple_sources", "attempts"}
PLACEHOLDERS = ("请填写", "请替换", "待填写", "TODO", "匿名代号")
SENSITIVE = (
    re.compile(r"/" r"Users/[^\s]+"),
    re.compile(r"(?i)\b(?:app_secret|access_token|refresh_token|api_key)\b\s*[:=]"),
    re.compile(r"(?i)\b(?:cli_|sk-|xox[baprs]-)[A-Za-z0-9_-]{12,}"),
)
TEACHER = re.compile(r"[王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾萧田董袁潘蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔汤]老师")
GENERIC_LABELS = {"很好", "聪明", "优秀", "乖", "听话", "正常", "全面发展", "健康成长", "提升能力", "改掉问题"}


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def iso_date(value: Any) -> date | None:
    if not is_text(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def months_between(birth: date, as_of: date) -> int:
    months = (as_of.year - birth.year) * 12 + as_of.month - birth.month
    if as_of.day < birth.day:
        months -= 1
    return months


def strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if isinstance(value, str):
        result.append((path, value))
    elif isinstance(value, dict):
        for key, item in value.items():
            result.extend(strings(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.extend(strings(item, f"{path}[{index}]"))
    return result


def validate(data: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["根节点必须是 JSON 对象"], warnings
    if data.get("schema_version") != SCHEMA:
        errors.append(f"schema_version 必须是 {SCHEMA}")
    track = data.get("plan_track")
    if track not in TRACKS:
        errors.append("plan_track 必须是 infant、preschool 或 school-age")

    as_of = iso_date(data.get("plan_as_of"))
    child = data.get("child") if isinstance(data.get("child"), dict) else {}
    birth = iso_date(child.get("birth_date"))
    if as_of is None or birth is None:
        errors.append("plan_as_of 和 child.birth_date 必须是有效 YYYY-MM-DD 日期")
    elif birth > as_of:
        errors.append("child.birth_date 不能晚于 plan_as_of")
    else:
        calculated = months_between(birth, as_of)
        if child.get("age_months") != calculated:
            errors.append(f"child.age_months 应为 {calculated}")
        if track in TRACKS:
            low, high = TRACKS[track]
            if not low <= calculated < high:
                errors.append(f"月龄 {calculated} 与 plan_track={track} 不匹配")
    if not is_text(child.get("id")):
        errors.append("child.id 必须是非空匿名代号")

    completed = data.get("completed_sections")
    if not isinstance(completed, list) or not REQUIRED_SECTIONS.issubset(set(completed)):
        errors.append("completed_sections 未覆盖全部必需主题")
    for field in ("family_goals", "strengths", "attempts"):
        value = data.get(field)
        if not isinstance(value, list) or not any(is_text(item) or isinstance(item, dict) for item in value):
            errors.append(f"{field} 至少需要一项")
    for field in ("family_goals", "strengths"):
        for index, item in enumerate(data.get(field) or []):
            if isinstance(item, str) and (item.strip() in GENERIC_LABELS or len(item.strip()) < 5):
                warnings.append(f"{field}[{index}] 可能只是笼统标签；应补充真实情境或证据，不能用来凑完整度")
    context = data.get("context")
    if not isinstance(context, dict) or not isinstance(context.get("routines"), list) or not context.get("routines"):
        errors.append("context.routines 至少需要一项")

    observations = data.get("observations")
    domains: set[str] = set()
    if not isinstance(observations, list) or len(observations) < 6:
        errors.append("observations 至少需要六条具体观察")
    else:
        for index, item in enumerate(observations):
            prefix = f"observations[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} 必须是对象")
                continue
            for field in ("domain", "observation", "source", "situation"):
                if not is_text(item.get(field)):
                    errors.append(f"{prefix}.{field} 必须是非空文本")
            if is_text(item.get("domain")):
                domains.add(item["domain"].strip())
        if len(domains) < 4:
            errors.append("observations 至少覆盖四个不同生活领域")

    sources = {item.get("source", "").strip() for item in observations or [] if isinstance(item, dict)}
    if len({source for source in sources if source}) < 2:
        warnings.append("当前只有一种来源；完整报告最好补充孩子、教师或其他照护者视角")
    for path, value in strings(data):
        if any(marker.lower() in value.lower() for marker in PLACEHOLDERS):
            errors.append(f"{path} 仍包含占位内容")
        if any(pattern.search(value) for pattern in SENSITIVE):
            errors.append(f"{path} 包含私有路径或疑似凭证")
        if TEACHER.search(value):
            warnings.append(f"{path} 疑似保留第三方姓名（“某老师”）：建议泛化为“教师/班主任”等角色")
    safety_flags = data.get("safety_flags")
    if isinstance(safety_flags, list) and safety_flags:
        warnings.append("safety_flags 非空：PASS 只代表结构合格；交接前必须人工判断是否暂停一般规划并优先处理安全风险")
    data_gaps = data.get("data_gaps")
    if isinstance(data_gaps, list) and data_gaps:
        warnings.append("data_gaps 非空：请核对 completed_sections 是否误把仍有关键缺口的主题标为完成")
    return sorted(set(errors)), sorted(set(warnings))


def sample(track: str, age_months: int, birth_date: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA,
        "plan_track": track,
        "plan_as_of": "2026-07-17",
        "child": {"id": "孩子A", "birth_date": birth_date, "age_months": age_months, "current_context": "家庭"},
        "completed_sections": sorted(REQUIRED_SECTIONS),
        "family_goals": ["让早晨更顺畅"],
        "child_goals": [],
        "strengths": ["愿意参与家庭任务"],
        "context": {"routines": ["早餐前准备"], "resources": [], "constraints": [], "languages": ["中文"]},
        "observations": [
            {"id": f"E{i:02d}", "domain": domain, "observation": f"事件{i}", "source": "家长" if i % 2 else "孩子", "observed_at": None, "situation": "家庭日常", "interpretation": None, "confidence": "medium", "unknowns": []}
            for i, domain in enumerate(("沟通", "关系", "日常", "游戏", "动作", "情绪"), 1)
        ],
        "attempts": ["尝试过图示提醒"], "professional_inputs": [], "contradictions": [], "data_gaps": [], "safety_flags": []
    }


def self_test() -> int:
    cases = (("infant", 23, "2024-07-18"), ("preschool", 47, "2022-07-18"), ("school-age", 95, "2018-07-18"))
    for track, age, birth in cases:
        errors, _ = validate(sample(track, age, birth))
        if errors:
            print(f"SELF-TEST FAIL {track}: {errors}", file=sys.stderr)
            return 1
    wrong = sample("infant", 47, "2022-07-18")
    errors, _ = validate(wrong)
    if not any("不匹配" in error for error in errors):
        print("SELF-TEST FAIL: cross-age case accepted", file=sys.stderr)
        return 1
    risky = sample("infant", 23, "2024-07-18")
    risky["safety_flags"] = ["报告者称出现能力倒退"]
    _, warnings = validate(risky)
    if not any("safety_flags" in warning for warning in warnings):
        print("SELF-TEST FAIL: safety flag warning missing", file=sys.stderr)
        return 1
    print("SELF-TEST PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.input is None:
        parser.error("input is required unless --self-test is used")
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(data)
    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("PASS" if not errors else "FAIL")
        for item in warnings:
            print(f"WARNING: {item}")
        for item in errors:
            print(f"ERROR: {item}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
