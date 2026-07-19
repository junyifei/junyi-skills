#!/usr/bin/env python3
"""Merge chunk distillations by semantic section in the public fixed order."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SECTIONS = [
    ("今日核心事件", ("今日核心事件",)),
    ("情绪地图", ("情绪地图",)),
    ("🎬 故事", ("🎬 故事", "🎬 故事/经历")),
    ("💡 观点", ("💡 观点", "💡 观点/论点")),
    ("🔥 金句", ("🔥 金句", "🔥 金句+语境")),
    ("🎭 场景", ("🎭 场景", "🎭 场景片段")),
    ("⚡ 冲突", ("⚡ 冲突", "⚡ 交锋/火花", "⚡ 冲突/交锋")),
    ("📊 数据案例", ("📊 数据案例", "📊 数据/案例")),
    ("🧭 决策原则", ("🧭 决策原则", "🧭 判断原则")),
    ("📋 工作待办安排", ("📋 工作待办安排", "📋 工作安排", "待办/决策")),
]

CANONICAL = [name for name, _ in SECTIONS]
ALIASES = {alias: name for name, aliases in SECTIONS for alias in aliases}
ITEM_SECTIONS = set(CANONICAL[2:9])
ISOLATED_MODES = {"isolated-worker", "fresh-session"}


def normalize_heading(raw: str) -> str | None:
    value = raw.strip().replace("（", "(").replace("）", ")")
    value = re.sub(r"\s+", " ", value)
    return ALIASES.get(value)


def section_blocks(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        name = normalize_heading(match.group(1))
        if not name:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((name, text[match.end() : end].strip()))
    return blocks


def extract_items(block: str) -> list[str]:
    matches = list(re.finditer(r"^####\s+\d+\.\s+.+?$", block, re.MULTILINE))
    items = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        item = block[match.start() : end].strip()
        item = re.sub(r"\n---\s*$", "", item).strip()
        if item:
            items.append(item)
    return items


def evidence_value(item: str) -> str:
    match = re.search(r"^\*\*证据位置\*\*[:：]\s*(.+)$", item, re.MULTILINE)
    return match.group(1).strip() if match else ""


def item_key(item: str) -> tuple[str, str]:
    first = item.splitlines()[0]
    title = re.sub(r"^####\s+\d+\.\s+", "", first)
    title = re.sub(r"[\s，。！？、:：\-—_]+", "", title).lower()
    return title, re.sub(r"\s+", "", evidence_value(item)).lower()


def deduplicate_items(items: list[str]) -> list[str]:
    chosen: dict[tuple[str, str], tuple[int, str]] = {}
    order: list[tuple[str, str]] = []
    for position, item in enumerate(items):
        key = item_key(item)
        if key not in chosen:
            chosen[key] = (position, item)
            order.append(key)
        elif len(item) > len(chosen[key][1]):
            chosen[key] = (chosen[key][0], item)
    return [chosen[key][1] for key in order]


def renumber(item: str, number: int) -> str:
    return re.sub(r"^####\s+\d+\.\s+", f"#### {number}. ", item, count=1)


def clean_list_lines(block: str) -> list[str]:
    lines = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---" or stripped.startswith("> 来源"):
            continue
        if re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            lines.append(stripped)
    return lines


def deduplicate_lines(lines: list[str]) -> list[str]:
    seen, result = set(), []
    for line in lines:
        key = re.sub(r"^[\-*\d.\s]+", "", line)
        key = re.sub(r"\s+", "", key).lower()
        if key and key not in seen:
            seen.add(key)
            result.append(line)
    return result


def work_content(block: str) -> tuple[list[str], list[str]]:
    rows, notes = [], []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue
        if stripped.startswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells and cells[0] not in {"类型", "事项"} and not all(
                re.fullmatch(r":?-{3,}:?", cell or "-") for cell in cells
            ):
                rows.append(stripped)
        elif stripped.startswith("> ⚠️") or "原文未形成明确待办" in stripped:
            notes.append(stripped)
    return rows, notes


def merge_texts(texts: list[str], title: str, source: str) -> str:
    collected: dict[str, list[str]] = {name: [] for name in CANONICAL}
    work_rows: list[str] = []
    work_notes: list[str] = []

    for text in texts:
        for name, block in section_blocks(text):
            if name in ITEM_SECTIONS:
                collected[name].extend(extract_items(block))
            elif name in {"今日核心事件", "情绪地图"}:
                collected[name].extend(clean_list_lines(block))
            else:
                rows, notes = work_content(block)
                work_rows.extend(rows)
                work_notes.extend(notes)

    parts = [f"# {title}"]
    if source:
        parts.extend(["", f"> 来源：{source}"])

    for name in CANONICAL:
        if name in ITEM_SECTIONS:
            items = deduplicate_items(collected[name])
            if not items:
                continue
            parts.extend(["", f"## {name}", ""])
            for index, item in enumerate(items, start=1):
                if index > 1:
                    parts.extend(["", "---", ""])
                parts.append(renumber(item, index))
        elif name in {"今日核心事件", "情绪地图"}:
            lines = deduplicate_lines(collected[name])
            if lines:
                parts.extend(["", f"## {name}", "", *lines])
        else:
            rows = deduplicate_lines(work_rows)
            notes = deduplicate_lines(work_notes)
            if not rows and not notes:
                continue
            parts.extend(["", f"## {name}", ""])
            if rows:
                parts.extend(
                    [
                        "| 类型 | 事项 | 责任人 | 时间线索 | 状态 | 证据位置 |",
                        "|---|---|---|---|---|---|",
                        *rows,
                    ]
                )
            if notes:
                if rows:
                    parts.append("")
                parts.extend(notes)

    return "\n".join(parts).rstrip() + "\n"


def validate_manifest_for_merge(data: dict) -> None:
    chunks = data.get("chunks", [])
    if not isinstance(chunks, list):
        raise ValueError("manifest chunks must be a list")
    isolation_required = len(chunks) >= 3
    isolation = data.get("isolation", {})
    if isolation_required:
        if not isinstance(isolation, dict):
            raise ValueError("manifest isolation must be an object")
        mode = isolation.get("mode")
        if isolation.get("required") is not True or mode not in ISOLATED_MODES:
            raise ValueError("three or more chunks require an assigned isolation mode")
        if isolation.get("orchestrator_read_raw_chunks") is not False:
            raise ValueError("orchestrator raw-chunk isolation was not preserved")
    for entry in data.get("chunks", []):
        status = entry.get("status")
        if status == "pending":
            raise ValueError(f"chunk {entry.get('chunk', '?')} is still pending")
        if status == "skipped" and not str(entry.get("skip_reason", "")).strip():
            raise ValueError(f"chunk {entry.get('chunk', '?')} skipped without reason")
        if status in {"distilled", "merged"} and isolation_required:
            if entry.get("worker_mode") != mode:
                raise ValueError(f"chunk {entry.get('chunk', '?')} missing matching worker mode")
            if not str(entry.get("worker_run", "")).strip():
                raise ValueError(f"chunk {entry.get('chunk', '?')} missing worker/run identifier")


def read_manifest_for_merge(manifest_path: Path) -> dict:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest_for_merge(data)
    return data


def update_manifest(manifest_path: Path, output: Path) -> None:
    data = read_manifest_for_merge(manifest_path)
    for entry in data.get("chunks", []):
        status = entry.get("status")
        if status == "distilled":
            entry["status"] = "merged"
    data["final_path"] = str(output.resolve())
    data["workflow_status"] = "merged"
    data["merged_at"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chunks_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default="内容蒸馏")
    parser.add_argument("--source", default="")
    parser.add_argument("--manifest", type=Path, help="Update completed chunk states after merge")
    args = parser.parse_args()

    try:
        if args.manifest:
            read_manifest_for_merge(args.manifest)
        files = sorted(args.chunks_dir.rglob("*.distilled.md"))
        if not files:
            raise FileNotFoundError(f"no *.distilled.md files under {args.chunks_dir}")
        texts = [path.read_text(encoding="utf-8") for path in files]
        result = merge_texts(texts, args.title, args.source)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
        if args.manifest:
            update_manifest(args.manifest, args.output)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Merged {len(files)} files into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
