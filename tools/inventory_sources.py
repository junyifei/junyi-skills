#!/usr/bin/env python3
"""Build a private, read-only inventory of Markdown source material."""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


IGNORED_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".cache"}
PRIVACY_RE = re.compile(
    r"手机号|身份证|家庭住址|微信号|真实姓名|客户原话|学员原话|孩子姓名|隐私|confidential|private",
    re.IGNORECASE,
)
THIRD_PARTY_RE = re.compile(
    r"转载|摘录|版权|仅供学习|课程笔记|读书笔记|书摘|原作者|第三方",
    re.IGNORECASE,
)


@dataclass
class SourceRecord:
    asset_id: str
    title: str
    relative_path: str
    absolute_path: str
    source_type: str
    top_level_area: str
    created: str
    modified: str
    status: str
    topics: str
    line_count: int
    char_count: int
    privacy_signal: bool
    third_party_signal: bool
    public_status: str
    processing_status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True)
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def discover_markdown(vault: Path) -> list[Path]:
    paths: list[Path] = []
    for current, dirnames, filenames in os.walk(vault):
        dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
        for filename in filenames:
            if filename.lower().endswith(".md"):
                paths.append((Path(current) / filename).resolve())
    return sorted(paths, key=lambda path: str(path).lower())


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(index for index in range(1, min(len(lines), 120)) if lines[index].strip() == "---")
    except StopIteration:
        return {}
    data: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([^:#]{1,40}):\s*(.*)$", line)
        if match:
            data[match.group(1).strip()] = match.group(2).strip().strip("\"'")
    return data


def first_title(text: str, fallback: str) -> str:
    for line in text.splitlines()[:160]:
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def classify_source(relative: str) -> str:
    rules = [
        ("公众号", "公众号"),
        ("小红书", "小红书"),
        ("视频号", "视频号"),
        ("朋友圈", "朋友圈"),
        ("教练", "教练对话"),
        ("咨询", "咨询"),
        ("访谈", "访谈"),
        ("答疑", "答疑"),
        ("会议", "会议"),
        ("课程", "课程与学习"),
        ("复盘", "复盘"),
        ("反馈", "案例与反馈"),
        ("案例", "案例与反馈"),
        ("觉知日记", "个人日记"),
        ("日常对话蒸馏", "个人日记"),
        ("Skill开发", "Skill研发"),
        ("方法论", "方法论"),
    ]
    for marker, result in rules:
        if marker in relative:
            return result
    return "其他"


def public_status(relative: str, frontmatter: dict[str, str]) -> str:
    combined = " ".join(frontmatter.values())
    if "公开版" in relative or "出口:公开" in combined or "出口:公域" in combined:
        return "public-candidate"
    if "私密" in relative or "不公开" in combined or "出口:自用" in combined:
        return "private"
    return "private-review"


def parse_date(value: str) -> str:
    match = re.search(r"20\d{2}-\d{1,2}-\d{1,2}", value or "")
    return match.group(0) if match else ""


def build_record(index: int, vault: Path, path: Path) -> SourceRecord:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter = parse_frontmatter(text)
    relative = str(path.relative_to(vault))
    modified = datetime.fromtimestamp(path.stat().st_mtime).astimezone().date().isoformat()
    created = parse_date(frontmatter.get("created", ""))
    topics = frontmatter.get("主题标签") or frontmatter.get("tags") or ""
    status = frontmatter.get("status", "")
    return SourceRecord(
        asset_id=f"AST{index:05d}",
        title=first_title(text, path.stem),
        relative_path=relative,
        absolute_path=str(path),
        source_type=classify_source(relative),
        top_level_area=Path(relative).parts[0] if Path(relative).parts else "",
        created=created,
        modified=modified,
        status=status,
        topics=topics,
        line_count=len(text.splitlines()),
        char_count=len(text),
        privacy_signal=bool(PRIVACY_RE.search(text)),
        third_party_signal=bool(THIRD_PARTY_RE.search(text)),
        public_status=public_status(relative, frontmatter),
        processing_status="inventoried",
    )


def write_csv(path: Path, records: list[SourceRecord]) -> None:
    rows = [asdict(record) for record in records]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def write_summary(path: Path, records: list[SourceRecord]) -> None:
    by_area = Counter(item.top_level_area for item in records)
    by_type = Counter(item.source_type for item in records)
    by_public = Counter(item.public_status for item in records)
    lines = [
        "# Obsidian 素材盘点摘要",
        "",
        f"- Markdown 素材：{len(records)}",
        f"- 总字符数：{sum(item.char_count for item in records):,}",
        f"- 隐私词命中：{sum(item.privacy_signal for item in records)}",
        f"- 第三方内容词命中：{sum(item.third_party_signal for item in records)}",
        "",
        "## 顶层区域",
        "",
        "| 区域 | 文件数 |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {count} |" for name, count in by_area.most_common())
    lines.extend(["", "## 素材类型", "", "| 类型 | 文件数 |", "|---|---:|"])
    lines.extend(f"| {name} | {count} |" for name, count in by_type.most_common())
    lines.extend(["", "## 公开状态", "", "| 状态 | 文件数 |", "|---|---:|"])
    lines.extend(f"| {name} | {count} |" for name, count in by_public.most_common())
    lines.extend(
        [
            "",
            "> 隐私与第三方内容均为关键词命中，不代表文件一定不能公开；必须阅读上下文后判断。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_privacy_report(path: Path, records: list[SourceRecord]) -> None:
    flagged = [item for item in records if item.privacy_signal or item.third_party_signal]
    lines = [
        "# 隐私与第三方内容复核队列",
        "",
        "| 素材 | 类型 | 隐私词 | 第三方词 | 当前公开状态 |",
        "|---|---|---:|---:|---|",
    ]
    for item in flagged:
        lines.append(
            f"| `{item.relative_path}` | {item.source_type} | {int(item.privacy_signal)} | "
            f"{int(item.third_party_signal)} | {item.public_status} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_batches(path: Path, records: list[SourceRecord]) -> None:
    grouped: dict[str, list[SourceRecord]] = defaultdict(list)
    for item in records:
        if item.public_status != "private":
            grouped[item.source_type].append(item)
    lines = [
        "# 建议蒸馏批次",
        "",
        "> 本清单仅安排盘点后的候选素材；进入蒸馏前仍需确认公开权限。每批最多 50 篇，或累计约 150,000 字符。",
        "",
    ]
    batch_number = 1
    for source_type, items in sorted(grouped.items(), key=lambda pair: pair[0]):
        current: list[SourceRecord] = []
        current_chars = 0
        for item in sorted(items, key=lambda value: (value.created or value.modified, value.relative_path)):
            if current and (len(current) >= 50 or current_chars + item.char_count > 150_000):
                lines.extend(render_batch(batch_number, source_type, current, current_chars))
                batch_number += 1
                current, current_chars = [], 0
            current.append(item)
            current_chars += item.char_count
        if current:
            lines.extend(render_batch(batch_number, source_type, current, current_chars))
            batch_number += 1
    path.write_text("\n".join(lines), encoding="utf-8")


def render_batch(number: int, source_type: str, items: list[SourceRecord], chars: int) -> list[str]:
    lines = [f"## B{number:03d} · {source_type} · {len(items)} 篇 · {chars:,} 字符", ""]
    lines.extend(f"- [ ] `{item.relative_path}`" for item in items)
    lines.append("")
    return lines


def main() -> None:
    args = parse_args()
    vault = Path(args.vault).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [
        build_record(index, vault, path)
        for index, path in enumerate(discover_markdown(vault), start=1)
    ]
    write_csv(output_dir / "sources-inventory.csv", records)
    write_summary(output_dir / "sources-summary.md", records)
    write_privacy_report(output_dir / "privacy-review-needed.md", records)
    write_batches(output_dir / "suggested-processing-batches.md", records)
    print(f"Inventoried {len(records)} Markdown files into {output_dir}")


if __name__ == "__main__":
    main()
