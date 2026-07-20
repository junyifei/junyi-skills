#!/usr/bin/env python3
"""Validate the eight-layer learning-distillation output contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


LAYERS = [
    "L1｜关键结论",
    "L2｜主张与证据地图",
    "L3｜用自己的话讲明白",
    "L4｜可迁移方法",
    "L5｜与我已有认知的关系",
    "L6｜应用与小实验",
    "L7｜存疑与待跟进",
    "L8｜一句话本质",
]


def layer_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(L[1-8]｜.+?)\s*$", text, re.MULTILINE))
    blocks = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1).strip(), text[match.end() : end].strip()))
    return blocks


def subsection_blocks(block: str) -> list[str]:
    matches = list(re.finditer(r"^###\s+.+?$", block, re.MULTILINE))
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        result.append(block[match.start() : end].strip())
    return result


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    if "\ufffd" in text:
        errors.append("contains U+FFFD replacement characters")

    blocks = layer_blocks(text)
    names = [name for name, _ in blocks]
    if names != LAYERS:
        errors.append(f"layers missing, duplicated, renamed, or out of order: {names}")

    block_map = {name: block for name, block in blocks}
    for layer in LAYERS:
        if layer in block_map and not block_map[layer].strip():
            errors.append(f"empty layer: {layer}")

    for item in subsection_blocks(block_map.get("L2｜主张与证据地图", "")):
        if not re.search(r"^\*\*证据位置\*\*[:：]", item, re.MULTILINE):
            errors.append(f"L2 item missing evidence position: {item.splitlines()[0]}")
        if not re.search(r"^\*\*类型\*\*[:：]", item, re.MULTILINE):
            errors.append(f"L2 item missing type: {item.splitlines()[0]}")
        if not re.search(r"^\*\*支持状态\*\*[:：]", item, re.MULTILINE):
            errors.append(f"L2 item missing support status: {item.splitlines()[0]}")

    for item in subsection_blocks(block_map.get("L4｜可迁移方法", "")):
        for field in ("前置条件", "不适用场景", "证据位置"):
            if not re.search(rf"^\*\*{field}\*\*[:：]", item, re.MULTILINE):
                errors.append(f"L4 method missing {field}: {item.splitlines()[0]}")

    for item in subsection_blocks(block_map.get("L6｜应用与小实验", "")):
        for field in ("要验证的假设", "最小动作", "观察信号", "停止/调整条件"):
            if not re.search(rf"^\*\*{re.escape(field)}\*\*[:：]", item, re.MULTILINE):
                errors.append(f"L6 experiment missing {field}: {item.splitlines()[0]}")

    l5 = block_map.get("L5｜与我已有认知的关系", "")
    if l5 and "个人应用背景：未提供" in text and not re.search(r"待使用者|未提供|可能关联", l5):
        errors.append("L5 invents certainty although personal application context was not provided")

    return errors


def resolve_path(value: str, manifest_path: Path) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else manifest_path.parent / candidate


def validate_manifest(manifest_path: Path) -> list[str]:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"manifest cannot be read: {exc}"]
    errors = []
    chunks = data.get("chunks", [])
    if data.get("chunk_count") != len(chunks):
        errors.append("manifest chunk_count does not match chunks list")
    source = resolve_path(str(data.get("source", "")), manifest_path)
    if not source.is_file():
        errors.append(f"source missing: {source}")
    for entry in chunks:
        number = entry.get("chunk", "?")
        source_chunk = resolve_path(str(entry.get("path", "")), manifest_path)
        if not source_chunk.is_file():
            errors.append(f"chunk {number} missing: {source_chunk}")
        status = entry.get("status")
        if status == "pending":
            errors.append(f"chunk {number} is still pending")
        elif status == "skipped" and not str(entry.get("skip_reason", "")).strip():
            errors.append(f"chunk {number} skipped without reason")
        elif status in {"ledgered", "merged"}:
            ledger = resolve_path(str(entry.get("ledger_path", "")), manifest_path)
            if not ledger.is_file():
                errors.append(f"chunk {number} ledger missing: {ledger}")
        elif status not in {"skipped", "ledgered", "merged"}:
            errors.append(f"chunk {number} invalid status: {status}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        text = args.input.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate_text(text)
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
