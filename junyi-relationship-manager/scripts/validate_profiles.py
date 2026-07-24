#!/usr/bin/env python3
"""Validate junyi-relationship-manager v2 Markdown profiles with stdlib only."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path


SCHEMA = "junyi-relationship/v2"
PERSON_ID = re.compile(r"^person_\d{8}_[a-z0-9]{8}$")
ALLOWED_TIERS = {"lite", "full"}
ALLOWED_STAGES = {"待确认", "认识", "熟悉", "信任", "深度", "核心"}
ALLOWED_SOURCES = {"unknown", "user_fact", "system_rule_new_contact"}
REQUIRED_FIELDS = {
    "schema_version",
    "person_id",
    "姓名",
    "身份标识",
    "身份标识来源",
    "档案级别",
    "圈层",
    "圈层来源",
    "亲密度",
    "亲密度来源",
    "关系阶段",
    "关系阶段来源",
    "最近更新",
}
LITE_SECTIONS = {"基本信息", "当前状态", "互动时间线", "当前需求", "待跟进"}
FULL_SECTIONS = LITE_SECTIONS | {"我的期待", "素材库", "关系里程碑"}
UNSAFE_FILENAME = re.compile(r"[/\\\x00-\x1f]")
DESIRE_WORDS = re.compile(r"希望|期待|想保持|想以后|愿望")
COMMITMENT_WORDS = re.compile(r"答应|承诺|约好|计划(?:在|于)|会在|要在|提醒我")


@dataclass
class Result:
    path: Path
    person_id: str | None
    errors: list[str]
    warnings: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "person_id": self.person_id,
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, text, ["缺少开头 YAML frontmatter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, text, ["缺少结束 YAML 分隔线"]
    metadata: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            errors.append(f"第 {number} 行不是简单的 key: value")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            errors.append(f"frontmatter 字段重复：{key}")
        metadata[key] = value.strip().strip('"\'')
    return metadata, "\n".join(lines[end + 1 :]), errors


def parse_closeness(raw: str | None) -> int | None | str:
    if raw in (None, "", "null", "待确认"):
        return None
    try:
        return int(raw)
    except ValueError:
        return "invalid"


def valid_iso_date(raw: str | None) -> bool:
    if not raw:
        return False
    try:
        date.fromisoformat(raw)
        return True
    except ValueError:
        return False


def section_names(body: str) -> set[str]:
    return {
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE)
    }


def validate_followup_semantics(body: str) -> list[str]:
    errors: list[str] = []
    in_followups = False
    status: str | None = None
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line == "## 待跟进":
            in_followups = True
            status = None
            continue
        if in_followups and line.startswith("## "):
            break
        if not in_followups:
            continue
        if line.startswith("- 状态："):
            status = line.split("：", 1)[1].strip()
        elif line.startswith("- 承诺原文：") and status == "open":
            promise = line.split("：", 1)[1].strip()
            if DESIRE_WORDS.search(promise) and not COMMITMENT_WORDS.search(promise):
                errors.append("“希望/期待/想保持”是关系意向，不能标为 open 承诺")
    return errors


def validate_file(path: Path) -> Result:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return Result(path, None, [f"无法读取 UTF-8 文件：{exc}"], [])

    metadata, body, parse_errors = parse_frontmatter(text)
    errors.extend(parse_errors)
    missing = sorted(REQUIRED_FIELDS - set(metadata))
    if missing:
        errors.append(f"缺少 frontmatter 字段：{', '.join(missing)}")

    schema = metadata.get("schema_version")
    if schema != SCHEMA:
        errors.append(f"schema_version 必须是 {SCHEMA}")

    person_id = metadata.get("person_id")
    if not person_id or not PERSON_ID.fullmatch(person_id):
        errors.append("person_id 必须符合 person_YYYYMMDD_8位小写字母数字")
    else:
        suffix = person_id.rsplit("_", 1)[-1]
        if not path.stem.endswith(f"--{suffix}"):
            errors.append(f"文件名必须以 --{suffix} 结尾")

    if UNSAFE_FILENAME.search(path.name) or ".." in path.name:
        errors.append("文件名包含不安全路径字符")
    if not metadata.get("姓名"):
        errors.append("姓名不能为空")
    if not metadata.get("身份标识"):
        errors.append("身份标识不能为空；未知时写待确认")

    tier = metadata.get("档案级别")
    if tier not in ALLOWED_TIERS:
        errors.append("档案级别必须是 lite 或 full")

    for field in ("身份标识来源", "圈层来源", "亲密度来源", "关系阶段来源"):
        source = metadata.get(field)
        if source not in ALLOWED_SOURCES:
            errors.append(f"{field} 必须是 unknown、user_fact 或 system_rule_new_contact")

    identity = metadata.get("身份标识")
    identity_source = metadata.get("身份标识来源")
    if identity == "待确认" and identity_source != "unknown":
        errors.append("身份标识为待确认时，身份标识来源必须是 unknown")
    if identity not in (None, "待确认") and identity_source != "user_fact":
        errors.append("已填写身份标识必须来自 user_fact")

    circle = metadata.get("圈层")
    circle_source = metadata.get("圈层来源")
    if circle == "待确认" and circle_source != "unknown":
        errors.append("圈层为待确认时，圈层来源必须是 unknown")
    if circle not in (None, "待确认") and circle_source != "user_fact":
        errors.append("已填写圈层必须来自 user_fact")

    closeness = parse_closeness(metadata.get("亲密度"))
    closeness_source = metadata.get("亲密度来源")
    if closeness == "invalid" or (isinstance(closeness, int) and not 1 <= closeness <= 5):
        errors.append("亲密度必须是 null 或 1—5 的整数")
    elif closeness is None and closeness_source != "unknown":
        errors.append("亲密度未知时，亲密度来源必须是 unknown")
    elif isinstance(closeness, int) and closeness_source != "user_fact":
        errors.append("已填写亲密度必须来自 user_fact")

    stage = metadata.get("关系阶段")
    stage_source = metadata.get("关系阶段来源")
    if stage not in ALLOWED_STAGES:
        errors.append("关系阶段值无效")
    elif stage == "待确认" and stage_source != "unknown":
        errors.append("关系阶段待确认时，来源必须是 unknown")
    elif stage == "认识" and stage_source not in {"user_fact", "system_rule_new_contact"}:
        errors.append("认识阶段只能来自 user_fact 或 system_rule_new_contact")
    elif stage not in {"待确认", "认识"} and stage_source != "user_fact":
        errors.append("熟悉及以上阶段必须来自 user_fact")

    if not valid_iso_date(metadata.get("最近更新")):
        errors.append("最近更新必须是有效 YYYY-MM-DD 日期")

    sections = section_names(body)
    required_sections = FULL_SECTIONS if tier == "full" else LITE_SECTIONS
    missing_sections = sorted(required_sections - sections)
    if missing_sections:
        errors.append(f"缺少正文章节：{', '.join(missing_sections)}")
    if tier == "lite" and sections & (FULL_SECTIONS - LITE_SECTIONS):
        warnings.append("lite 档案包含完整档案章节；如为有意深度建档，请改为 full")
    if tier == "full" and isinstance(closeness, int) and closeness < 4:
        warnings.append("亲密度低于 4 的 full 档案需要用户明确要求完整建档")

    if "系统建议（不写成事实）" not in body:
        warnings.append("建议保留“系统建议（不写成事实）”字段，防止建议混入人物事实")
    errors.extend(validate_followup_semantics(body))

    return Result(path, person_id, sorted(set(errors)), sorted(set(warnings)))


def collect_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if target.is_dir():
        return sorted(path for path in target.rglob("*.md") if path.is_file())
    raise FileNotFoundError(target)


def validate_target(target: Path) -> list[Result]:
    paths = collect_paths(target)
    results = [validate_file(path) for path in paths]
    by_id: dict[str, list[Result]] = {}
    for result in results:
        if result.person_id:
            by_id.setdefault(result.person_id, []).append(result)
    for person_id, matches in by_id.items():
        if len(matches) > 1:
            locations = ", ".join(str(item.path) for item in matches)
            for item in matches:
                item.errors.append(f"person_id 重复：{person_id} 出现在 {locations}")
                item.errors.sort()
    return results


def render_text(results: list[Result]) -> None:
    if not results:
        print("WARNING: 没有找到 Markdown 档案")
        return
    for result in results:
        print(f"{'PASS' if result.valid else 'FAIL'} {result.path}")
        for warning in result.warnings:
            print(f"  WARNING: {warning}")
        for error in result.errors:
            print(f"  ERROR: {error}")
    passed = sum(result.valid for result in results)
    print(f"RESULT {passed} passed, {len(results) - passed} failed")


def profile_text(*, person_id: str, tier: str = "lite", closeness: str = "null") -> str:
    extra = ""
    if tier == "full":
        extra = "\n## 我的期待\n\n- 待确认\n\n## 素材库\n\n- 待确认\n\n## 关系里程碑\n\n- 待确认\n"
    closeness_source = "user_fact" if closeness != "null" else "unknown"
    return f"""---
schema_version: {SCHEMA}
person_id: {person_id}
姓名: 测试人物
身份标识: 测试身份
身份标识来源: user_fact
档案级别: {tier}
圈层: 待确认
圈层来源: unknown
亲密度: {closeness}
亲密度来源: {closeness_source}
关系阶段: 认识
关系阶段来源: system_rule_new_contact
最近更新: 2026-07-24
---

# 测试人物 · 测试身份

## 基本信息

- 测试

## 当前状态

- 系统建议（不写成事实）：无

## 互动时间线

- 测试

## 当前需求

- 状态：unknown

## 待跟进

- 状态：unknown
{extra}"""


def self_test() -> int:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append((name, condition, detail))

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        valid_id = "person_20260724_ab12cd34"
        valid = root / "测试人物--测试身份--ab12cd34.md"
        valid.write_text(profile_text(person_id=valid_id), encoding="utf-8")
        result = validate_file(valid)
        check("valid lite profile", result.valid, str(result.errors))

        full_id = "person_20260724_ef56gh78"
        full = root / "测试人物--测试身份--ef56gh78.md"
        full.write_text(profile_text(person_id=full_id, tier="full", closeness="4"), encoding="utf-8")
        result = validate_file(full)
        check("valid full profile", result.valid, str(result.errors))

        bad_source_id = "person_20260724_ij90kl12"
        bad_source = root / "测试人物--测试身份--ij90kl12.md"
        bad_source.write_text(
            profile_text(person_id=bad_source_id).replace("圈层: 待确认", "圈层: 外圈"),
            encoding="utf-8",
        )
        result = validate_file(bad_source)
        check("reject inferred circle", any("圈层" in item and "user_fact" in item for item in result.errors), str(result.errors))

        bad_stage_id = "person_20260724_mn34op56"
        bad_stage = root / "测试人物--测试身份--mn34op56.md"
        bad_stage.write_text(
            profile_text(person_id=bad_stage_id).replace("关系阶段: 认识", "关系阶段: 熟悉"),
            encoding="utf-8",
        )
        result = validate_file(bad_stage)
        check("reject automatic stage upgrade", any("熟悉及以上" in item for item in result.errors), str(result.errors))

        desire_id = "person_20260724_qr78st90"
        desire = root / "测试人物--测试身份--qr78st90.md"
        desire.write_text(
            profile_text(person_id=desire_id).replace(
                "- 状态：unknown\n",
                "- 状态：open\n- 承诺原文：我希望以后每月和她交流一次。\n",
            ),
            encoding="utf-8",
        )
        result = validate_file(desire)
        check("reject desire as open follow-up", any("关系意向" in item for item in result.errors), str(result.errors))

        duplicate = root / "另一个人--测试身份--ab12cd34.md"
        duplicate.write_text(profile_text(person_id=valid_id), encoding="utf-8")
        results = validate_target(root)
        check(
            "detect duplicate person id",
            sum(any("person_id 重复" in error for error in item.errors) for item in results) == 2,
            str([item.errors for item in results]),
        )

    for name, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {name}{'' if passed else f': {detail}'}")
    failures = sum(not passed for _, passed, _ in checks)
    print(f"RESULT {len(checks) - failures} passed, {failures} failed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.target is None:
        parser.error("target is required unless --self-test is used")
    try:
        results = validate_target(args.target)
    except (OSError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps([result.as_dict() for result in results], ensure_ascii=False, indent=2))
    else:
        render_text(results)
    return 0 if results and all(result.valid for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
