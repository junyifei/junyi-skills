#!/usr/bin/env python3
"""Run structural, evidence-language, portability, and plain-language checks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SECTION_GROUPS = {
    "decision": ("决策先行", "推荐方向"),
    "evidence": ("证据", "事实"),
    "layers": ("五层定位", "传播入口"),
    "audience": ("触达人群", "真正买方"),
    "change": ("用户从之前到之后", "用户变化"),
    "content": ("内容、故事与证明", "内容支柱"),
    "business": ("产品与商业", "最小付费"),
    "comparison": ("候选比较", "基础检查"),
    "validation": ("30 天", "90 天"),
}

EVIDENCE_MARKERS = ("【事实", "【推断", "【假设", "【未知")

PLAIN_LANGUAGE = (
    "用户在什么情况下会想起你",
    "成为主定位前必须通过的基础检查",
    "什么情况说明这条路不成立",
)


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

    errors: list[str] = []
    warnings: list[str] = []

    if args.book.suffix.lower() not in {".md", ".markdown"}:
        warnings.append("output is not a Markdown file")

    if not re.search(r"^#\s+.+", text, flags=re.MULTILINE):
        errors.append("missing H1 title")

    for label, alternatives in SECTION_GROUPS.items():
        if not any(term in text for term in alternatives):
            errors.append(f"missing required content group: {label} ({' / '.join(alternatives)})")

    for marker in EVIDENCE_MARKERS:
        if marker not in text:
            errors.append(f"missing evidence label: {marker}】")

    for phrase in PLAIN_LANGUAGE:
        if phrase not in text:
            errors.append(f"missing preferred plain-language phrase: {phrase}")

    if re.search(r"/Users/[^\s)]+|[A-Za-z]:\\Users\\", text):
        errors.append("contains a machine-specific absolute user path")

    for name in args.forbid_name:
        if name and name in text:
            errors.append(f"forbidden case-specific name appears: {name}")

    if "已验证" in text and not any(
        term in text for term in ("付款", "定金", "复购", "续费", "转介绍", "重复购买")
    ):
        warnings.append("uses 已验证 without an obvious costly-commitment term; review payment evidence")

    if "100" not in text or not any(term in text for term in ("内容燃料", "100 题", "100条", "100 条")):
        warnings.append("100-topic content-fuel check is not visible")

    if not any(term in text for term in ("不需要吸引", "排除人群", "不适配人群")):
        warnings.append("excluded or non-target audiences are not explicit")

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
