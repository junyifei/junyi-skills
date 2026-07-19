#!/usr/bin/env python3
"""Validate the public content-distillation contract and optional resume manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ORDER = [
    "今日核心事件",
    "情绪地图",
    "🎬 故事",
    "💡 观点",
    "🔥 金句",
    "🎭 场景",
    "⚡ 冲突",
    "📊 数据案例",
    "🧭 决策原则",
    "📋 工作待办安排",
]
ITEM_SECTIONS = set(ORDER[2:9])
ISOLATED_MODES = {"isolated-worker", "fresh-session"}


def heading_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match.group(1).strip(), text[match.end() : end].strip()))
    return result


def item_blocks(block: str) -> list[str]:
    matches = list(re.finditer(r"^####\s+\d+\.\s+.+?$", block, re.MULTILINE))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        result.append(block[match.start() : end].strip())
    return result


def validate_text(text: str, daily: bool = False) -> list[str]:
    errors: list[str] = []
    if "\ufffd" in text:
        errors.append("contains U+FFFD replacement characters")

    blocks = heading_blocks(text)
    names = [name for name, _ in blocks]
    known = [name for name in names if name in ORDER]
    positions = [ORDER.index(name) for name in known]
    if positions != sorted(positions):
        errors.append("sections are not in the fixed order")
    for name in ORDER:
        count = names.count(name)
        if count > 1:
            errors.append(f"section appears more than once: {name}")

    if daily:
        for required in ("今日核心事件", "情绪地图", "📋 工作待办安排"):
            if required not in names:
                errors.append(f"daily mode missing required section: {required}")

    block_map = {name: block for name, block in blocks}
    for name in ITEM_SECTIONS:
        if name not in block_map:
            continue
        items = item_blocks(block_map[name])
        if not items:
            errors.append(f"section has no numbered items: {name}")
            continue
        expected = list(range(1, len(items) + 1))
        actual = [int(re.match(r"^####\s+(\d+)\.", item).group(1)) for item in items]
        if actual != expected:
            errors.append(f"item numbering is not consecutive in {name}: {actual}")
        for index, item in enumerate(items, start=1):
            if not re.search(r"^\*\*证据位置\*\*[:：]", item, re.MULTILINE):
                errors.append(f"{name} item {index} missing evidence position")
            if "📎 **原话**" not in item:
                errors.append(f"{name} item {index} missing original quote block")
            quote_pos = item.find("📎 **原话**")
            if quote_pos >= 0 and not re.search(r"^>\s*\S+", item[quote_pos:], re.MULTILINE):
                errors.append(f"{name} item {index} has no blockquote after original quote label")

    if re.search(r"说话人\s*\d+", text):
        errors.append("contains unresolved speaker-number labels")

    for name, block in blocks:
        if name != "📋 工作待办安排" and re.search(r"^\|\s*(?:类型|事项)\s*\|", block, re.MULTILINE):
            errors.append(f"work/todo table appears outside final work section: {name}")

    work = block_map.get("📋 工作待办安排", "")
    if work:
        for line_number, line in enumerate(work.splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells[0] == "类型" or all(re.fullmatch(r":?-{3,}:?", cell or "-") for cell in cells):
                continue
            if len(cells) != 6:
                errors.append(f"work table row {line_number} must have 6 columns")

    return errors


def resolve_manifest_path(value: str, manifest_path: Path) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else manifest_path.parent / candidate


def validate_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"manifest cannot be read: {exc}"]

    chunks = data.get("chunks")
    if not isinstance(chunks, list):
        return ["manifest chunks must be a list"]
    if data.get("chunk_count") != len(chunks):
        errors.append("manifest chunk_count does not match chunks list")

    isolation_required = len(chunks) >= 3
    isolation = data.get("isolation")
    if not isinstance(isolation, dict):
        if isolation_required:
            errors.append("manifest isolation must be an object")
        isolation = {}
    if isolation_required:
        if isolation.get("required") is not True:
            errors.append("three or more chunks require isolation")
        mode = isolation.get("mode")
        if mode not in ISOLATED_MODES:
            errors.append("isolation mode must be isolated-worker or fresh-session")
        if isolation.get("orchestrator_read_raw_chunks") is not False:
            errors.append("orchestrator must declare that it did not read raw chunks")
    elif isolation and isolation.get("required") is not False:
        errors.append("isolation.required must be false for fewer than three chunks")

    source = resolve_manifest_path(str(data.get("source", "")), manifest_path)
    if not source.is_file():
        errors.append(f"manifest source missing: {source}")

    for entry in chunks:
        number = entry.get("chunk", "?")
        path = resolve_manifest_path(str(entry.get("path", "")), manifest_path)
        if not path.is_file():
            errors.append(f"chunk {number} source file missing: {path}")
        status = entry.get("status")
        reason = str(entry.get("skip_reason", "")).strip()
        if status == "pending":
            errors.append(f"chunk {number} is still pending")
        elif status == "skipped" and not reason:
            errors.append(f"chunk {number} skipped without reason")
        elif status in {"distilled", "merged"}:
            distilled = resolve_manifest_path(str(entry.get("distilled_path", "")), manifest_path)
            if not distilled.is_file():
                errors.append(f"chunk {number} missing distilled output: {distilled}")
            if isolation_required:
                worker_mode = entry.get("worker_mode")
                worker_run = str(entry.get("worker_run", "")).strip()
                if worker_mode not in ISOLATED_MODES:
                    errors.append(f"chunk {number} missing isolated worker mode")
                elif worker_mode != isolation.get("mode"):
                    errors.append(f"chunk {number} worker mode differs from manifest isolation mode")
                if not worker_run:
                    errors.append(f"chunk {number} missing worker/run identifier")
        elif status not in {"skipped", "distilled", "merged"}:
            errors.append(f"chunk {number} has invalid status: {status}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--daily", action="store_true", help="Require daily-only sections")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    try:
        text = args.input.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_text(text, daily=args.daily)
    if args.manifest:
        errors.extend(validate_manifest(args.manifest))

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
