#!/usr/bin/env python3
"""Validate the canonical B00-B11 Markdown personal-IP strategy book."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHAPTERS = [f"B{i:02d}" for i in range(12)]
CHAPTER_RE = re.compile(r"^##\s+(B\d{2})[｜|:]", flags=re.MULTILINE)

EVIDENCE_MARKERS = ("【事实", "【推断", "【假设", "【未知")

PLAIN_LANGUAGE = (
    "用户在什么情况下会想起你",
    "成为主定位前必须通过的基础检查",
    "什么情况说明这条路不成立",
)

B00_TERMS = (
    "用户在什么情况下会想起你",
    "触达人群",
    "真正买方",
    "不需要吸引的人",
    "传播入口",
    "人物标签",
    "内容承诺",
    "商业落点",
    "长期价值观",
    "表达身位",
    "内容主线",
    "当前信心",
    "待验证假设",
    "什么情况说明这条路不成立",
)

B09_TERMS = ("隐私边界", "真实性边界", "伦理边界", "产品边界", "能力边界")


def chapter_body(text: str, chapter: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(chapter)}[｜|:].*?(?=^##\s+B\d{{2}}[｜|:]|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(0) if match else ""


def check_text(text: str, *, forbid_names: list[str] | None = None) -> tuple[list[str], list[str]]:
    """Return structural errors and review warnings for a strategy book."""
    errors: list[str] = []
    warnings: list[str] = []

    if not re.search(r"^#\s+.+", text, flags=re.MULTILINE):
        errors.append("missing H1 title")

    found_chapters = CHAPTER_RE.findall(text)
    if found_chapters != CHAPTERS:
        errors.append(
            "chapters must appear exactly once and in order B00-B11; "
            f"found: {', '.join(found_chapters) or 'none'}"
        )

    b00 = chapter_body(text, "B00")
    for term in B00_TERMS:
        if term not in b00:
            errors.append(f"B00 missing required field: {term}")

    b09 = chapter_body(text, "B09")
    for term in B09_TERMS:
        if term not in b09:
            errors.append(f"B09 missing required boundary: {term}")

    for marker in EVIDENCE_MARKERS:
        if marker not in text:
            errors.append(f"missing evidence label: {marker}】")

    for phrase in PLAIN_LANGUAGE:
        if phrase not in text:
            errors.append(f"missing preferred plain-language phrase: {phrase}")

    if re.search(r"/Users/[^\s)]+|[A-Za-z]:\\Users\\", text):
        errors.append("contains a machine-specific absolute user path")

    for name in forbid_names or []:
        if name and name in text:
            errors.append(f"forbidden case-specific name appears: {name}")

    if "已验证" in text and not any(
        term in text for term in ("付款", "定金", "复购", "续费", "转介绍", "重复购买")
    ):
        warnings.append("uses 已验证 without an obvious costly-commitment term; review payment evidence")

    if "100" not in text or not any(term in text for term in ("内容燃料", "100 题", "100条", "100 条")):
        warnings.append("100-topic content-fuel check is not visible")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a full Markdown personal-IP strategy book.")
    parser.add_argument("book", type=Path, help="Markdown strategy book")
    parser.add_argument(
        "--forbid-name", action="append", default=[], help="Fail when a case-specific name appears"
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.book.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.book}", file=sys.stderr)
        return 2

    if args.book.suffix.lower() not in {".md", ".markdown"}:
        suffix_warnings = ["output is not a Markdown file"]
    else:
        suffix_warnings = []

    errors, warnings = check_text(text, forbid_names=args.forbid_name)
    warnings = suffix_warnings + warnings

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors or (args.strict and warnings):
        return 1
    print(
        f"PASS: {args.book} ({len(text)} chars, {len(errors)} errors, {len(warnings)} warnings)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
