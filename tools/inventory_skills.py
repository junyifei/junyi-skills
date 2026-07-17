#!/usr/bin/env python3
"""Inventory SKILL.md files without modifying source skills.

The generated reports may contain absolute paths and private-work indicators.
Write them to the repository's gitignored .private-inventory directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    ".obsidian",
    "node_modules",
    "__pycache__",
    ".cache",
    "dist",
    "build",
}

BACKUP_MARKERS = (
    "/_sync备份_",
    "/_待确认删除/",
    "/temp/",
    "/tmp/",
    "/legacy/",
    "/backup/",
)

HARD_CODED_PATH_RE = re.compile(
    r"/Users/|/home/|[A-Za-z]:\\\\Users\\\\|~/(?:\.openclaw|\.codex|\.claude|\.agents)"
)
CREDENTIAL_TERM_RE = re.compile(
    r"api[_ -]?key|app[_ -]?secret|client[_ -]?secret|password|private[_ -]?key|access[_ -]?token",
    re.IGNORECASE,
)
EXTERNAL_COMMAND_RE = re.compile(
    r"\b(?:curl|wget|npm|npx|pip|brew|git clone|bash|sh|python3?)\b",
    re.IGNORECASE,
)
PRIVATE_TERM_RE = re.compile(
    r"客户|学员|孩子姓名|真实姓名|手机号|微信号|身份证|家庭住址|个人隐私|private|confidential",
    re.IGNORECASE,
)


@dataclass
class SkillRecord:
    record_id: str
    name: str
    version: str
    description: str
    source_group: str
    skill_path: str
    skill_dir: str
    line_count: int
    file_count: int
    has_references: bool
    has_scripts: bool
    has_assets: bool
    has_agents_metadata: bool
    has_tests: bool
    frontmatter_valid: bool
    exact_hash: str
    same_name_count: int = 0
    exact_duplicate_count: int = 0
    path_status: str = "review"
    hardcoded_path_signal: bool = False
    credential_term_signal: bool = False
    external_command_signal: bool = False
    private_term_signal: bool = False
    license_signal: str = ""
    recommended_action: str = "review"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Scan root. Repeat for multiple roots; earlier roots have priority.",
    )
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


def parse_roots(values: list[str]) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --root value: {value!r}; expected LABEL=PATH")
        label, raw_path = value.split("=", 1)
        path = Path(raw_path).expanduser().resolve()
        if path.is_dir():
            roots.append((label.strip(), path))
    return roots


def discover_skill_files(roots: list[tuple[str, Path]]) -> list[tuple[str, Path]]:
    discovered: dict[Path, tuple[str, Path]] = {}
    for label, root in roots:
        for current, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in IGNORED_DIRS]
            if "SKILL.md" not in filenames:
                continue
            path = (Path(current) / "SKILL.md").resolve()
            discovered.setdefault(path, (label, path))
    return sorted(discovered.values(), key=lambda item: str(item[1]).lower())


def parse_frontmatter(text: str) -> tuple[dict[str, str], bool]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, False

    data: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in {"|", ">"}:
            block: list[str] = []
            index += 1
            while index < end and (lines[index].startswith(" ") or not lines[index].strip()):
                block.append(lines[index].strip())
                index += 1
            data[key] = " ".join(part for part in block if part).strip()
            continue
        data[key] = value.strip("\"'")
        index += 1
    valid = bool(data.get("name") and data.get("description"))
    return data, valid


def source_status(source_group: str, path: Path) -> str:
    normalized = "/" + str(path).replace("\\", "/").strip("/") + "/"
    if any(marker in normalized for marker in BACKUP_MARKERS):
        return "archive-or-retired"
    if source_group in {"primary_repo", "published_ip_bundle"}:
        return "already-public"
    if source_group == "obsidian":
        return "private-review"
    if source_group in {
        "codex_installed",
        "agents_installed",
        "openclaw_workspace",
        "openclaw_shared",
        "claude_installed",
    }:
        return "installed-origin-unknown"
    return "review"


def recommendation(record: SkillRecord) -> str:
    if record.path_status == "archive-or-retired":
        return "exclude-from-candidate-pool"
    if not record.frontmatter_valid:
        return "repair-frontmatter-before-review"
    if record.path_status == "already-public":
        return "retain-and-run-public-release-audit"
    if record.path_status == "private-review":
        return "confirm-rights-and-privacy-before-promotion"
    if record.path_status == "installed-origin-unknown":
        return "verify-authorship-and-canonical-source"
    return "review-for-canonical-source"


def license_signal(skill_dir: Path, frontmatter: dict[str, str]) -> str:
    if frontmatter.get("license"):
        return frontmatter["license"]
    for candidate in (skill_dir / "LICENSE", skill_dir.parent / "LICENSE"):
        if candidate.is_file():
            try:
                first = candidate.read_text(encoding="utf-8", errors="replace").splitlines()[0]
                return first[:120]
            except OSError:
                pass
    return ""


def build_record(index: int, source_group: str, skill_path: Path) -> SkillRecord:
    raw = skill_path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    frontmatter, frontmatter_valid = parse_frontmatter(text)
    skill_dir = skill_path.parent
    files = [path for path in skill_dir.rglob("*") if path.is_file() and ".git" not in path.parts]
    record = SkillRecord(
        record_id=f"SK{index:04d}",
        name=frontmatter.get("name") or skill_dir.name,
        version=frontmatter.get("version", ""),
        description=frontmatter.get("description", ""),
        source_group=source_group,
        skill_path=str(skill_path),
        skill_dir=str(skill_dir),
        line_count=len(text.splitlines()),
        file_count=len(files),
        has_references=(skill_dir / "references").is_dir(),
        has_scripts=(skill_dir / "scripts").is_dir(),
        has_assets=(skill_dir / "assets").is_dir(),
        has_agents_metadata=(skill_dir / "agents" / "openai.yaml").is_file(),
        has_tests=any((skill_dir / name).is_dir() for name in ("tests", "evals", "examples")),
        frontmatter_valid=frontmatter_valid,
        exact_hash=hashlib.sha256(raw).hexdigest(),
        path_status=source_status(source_group, skill_path),
        hardcoded_path_signal=bool(HARD_CODED_PATH_RE.search(text)),
        credential_term_signal=bool(CREDENTIAL_TERM_RE.search(text)),
        external_command_signal=bool(EXTERNAL_COMMAND_RE.search(text)),
        private_term_signal=bool(PRIVATE_TERM_RE.search(text)),
        license_signal=license_signal(skill_dir, frontmatter),
    )
    record.recommended_action = recommendation(record)
    return record


def candidate_score(record: SkillRecord) -> int:
    source_scores = {
        "primary_repo": 100,
        "published_ip_bundle": 90,
        "obsidian": 55,
        "documents": 40,
        "desktop": 35,
        "openclaw_workspace": 25,
        "openclaw_shared": 25,
        "codex_installed": 20,
        "agents_installed": 20,
        "claude_installed": 20,
    }
    score = source_scores.get(record.source_group, 0)
    if record.name.startswith("junyi-"):
        score += 25
    if "Skill开发" in record.skill_path or "million-follower-ip-skills" in record.skill_path:
        score += 20
    if record.has_references:
        score += 5
    if record.has_scripts:
        score += 5
    if record.has_tests:
        score += 10
    if record.path_status == "archive-or-retired":
        score -= 200
    if not record.frontmatter_valid:
        score -= 40
    return score


def choose_canonical(records: list[SkillRecord]) -> dict[str, SkillRecord]:
    by_name: dict[str, list[SkillRecord]] = defaultdict(list)
    for record in records:
        by_name[record.name].append(record)
    return {
        name: sorted(group, key=lambda item: (-candidate_score(item), item.skill_path))[0]
        for name, group in by_name.items()
    }


def write_csv(path: Path, records: list[SkillRecord]) -> None:
    rows = [asdict(record) for record in records]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def write_summary(path: Path, records: list[SkillRecord]) -> None:
    source_counts = Counter(record.source_group for record in records)
    status_counts = Counter(record.path_status for record in records)
    unique_names = len({record.name for record in records})
    duplicate_name_groups = sum(1 for count in Counter(record.name for record in records).values() if count > 1)
    exact_duplicate_groups = sum(1 for count in Counter(record.exact_hash for record in records).values() if count > 1)
    lines = [
        "# Skill 资产盘点摘要",
        "",
        f"- 扫描时间：{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}",
        f"- SKILL.md 实例：{len(records)}",
        f"- 唯一 Skill 名称：{unique_names}",
        f"- 同名重复组：{duplicate_name_groups}",
        f"- 内容完全相同重复组：{exact_duplicate_groups}",
        "",
        "## 来源分布",
        "",
        "| 来源 | 数量 |",
        "|---|---:|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in source_counts.most_common())
    lines.extend(["", "## 路径状态", "", "| 状态 | 数量 |", "|---|---:|"])
    lines.extend(f"| {key} | {value} |" for key, value in status_counts.most_common())
    lines.extend(
        [
            "",
            "> 本报告只代表自动发现结果，不代表作者权属、公开许可或质量已经确认。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_duplicates(path: Path, records: list[SkillRecord]) -> None:
    by_name: dict[str, list[SkillRecord]] = defaultdict(list)
    by_hash: dict[str, list[SkillRecord]] = defaultdict(list)
    for record in records:
        by_name[record.name].append(record)
        by_hash[record.exact_hash].append(record)
    lines = ["# Skill 重复报告", "", "## 同名 Skill", ""]
    for name, group in sorted(by_name.items()):
        if len(group) < 2:
            continue
        lines.append(f"### {name}（{len(group)} 份）")
        lines.extend(f"- `{item.skill_path}` · {item.source_group} · {item.path_status}" for item in group)
        lines.append("")
    lines.extend(["## 内容完全相同", ""])
    for digest, group in sorted(by_hash.items()):
        if len(group) < 2:
            continue
        lines.append(f"### `{digest[:12]}`（{len(group)} 份）")
        lines.extend(f"- `{item.skill_path}`" for item in group)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_risks(path: Path, records: list[SkillRecord]) -> None:
    risky = [
        record
        for record in records
        if record.hardcoded_path_signal
        or record.credential_term_signal
        or record.private_term_signal
        or record.external_command_signal
        or not record.frontmatter_valid
    ]
    lines = [
        "# Skill 公开前风险信号",
        "",
        "> 这些是文本命中信号，不等于真实泄密或恶意行为；发布前需人工复核命中上下文。",
        "",
        "| Skill | 来源 | 路径 | 绝对路径 | 凭据词 | 隐私词 | 外部命令 | Frontmatter |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for item in risky:
        lines.append(
            f"| {item.name} | {item.source_group} | `{item.skill_path}` | "
            f"{int(item.hardcoded_path_signal)} | {int(item.credential_term_signal)} | "
            f"{int(item.private_term_signal)} | {int(item.external_command_signal)} | "
            f"{int(item.frontmatter_valid)} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_candidates(path: Path, records: list[SkillRecord]) -> None:
    canonical = choose_canonical(records)
    candidates = sorted(canonical.values(), key=lambda item: (-candidate_score(item), item.name))
    eligible = [
        item
        for item in candidates
        if item.path_status != "archive-or-retired"
        and (
            item.source_group in {"primary_repo", "published_ip_bundle", "obsidian", "documents", "desktop"}
            or item.name.startswith("junyi-")
        )
    ]
    lines = [
        "# v0.1 自动候选池",
        "",
        "> 排名依据是来源、命名、资源完整度和路径状态；它不是发布批准。每项仍需权属、隐私、测试与安全审计。",
        "",
        "| 排名 | Skill | 分数 | 来源 | 当前路径状态 | 建议动作 |",
        "|---:|---|---:|---|---|---|",
    ]
    for index, item in enumerate(eligible[:30], start=1):
        lines.append(
            f"| {index} | `{item.name}` | {candidate_score(item)} | {item.source_group} | "
            f"{item.path_status} | {item.recommended_action} |"
        )
    lines.extend(["", "## 前 12 项的正式晋级门槛", ""])
    lines.extend(
        [
            "- 确认君一拥有公开与再许可所需权利。",
            "- 清除绝对路径、凭据、客户与家庭隐私。",
            "- 确认唯一规范来源，处理同名与完全重复副本。",
            "- 至少准备 2 个典型任务、1 个信息不足任务、1 个不应触发任务和 1 个边界任务。",
            "- 通过对应 Agent 的结构验证和独立盲测。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    roots = parse_roots(args.root)
    if not roots:
        raise SystemExit("No valid scan roots")
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    discovered = discover_skill_files(roots)
    records = [build_record(index, label, path) for index, (label, path) in enumerate(discovered, start=1)]
    name_counts = Counter(record.name for record in records)
    hash_counts = Counter(record.exact_hash for record in records)
    for record in records:
        record.same_name_count = name_counts[record.name]
        record.exact_duplicate_count = hash_counts[record.exact_hash]

    write_csv(output_dir / "skills-inventory.csv", records)
    write_summary(output_dir / "summary.md", records)
    write_duplicates(output_dir / "duplicate-report.md", records)
    write_risks(output_dir / "security-and-privacy-report.md", records)
    write_candidates(output_dir / "v0.1-candidates.md", records)
    (output_dir / "scan-manifest.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                "roots": [{"label": label, "path": str(path)} for label, path in roots],
                "record_count": len(records),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Inventoried {len(records)} SKILL.md files into {output_dir}")


if __name__ == "__main__":
    main()
