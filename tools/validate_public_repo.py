#!/usr/bin/env python3
"""Validate the tracked public surface of junyi-skills with stdlib only."""

from __future__ import annotations

import json
import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_INDEX = ROOT / "skill-index.json"
VERSION_FILE = ROOT / "VERSION"
README_FILE = ROOT / "README.md"
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SENSITIVE_PATTERNS = {
    "macOS user path": re.compile(r"/" r"Users/[^/\s]+/"),
    "possible API key assignment": re.compile(
        r"(?i)(api[_-]?key|access[_-]?token|app[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}"
    ),
    "private Feishu folder token": re.compile(r"feishu\.cn/(?:drive/folder|wiki)/[A-Za-z0-9]{12,}"),
}


def git_files(pattern: str | None = None, *, include_untracked: bool = False) -> list[str]:
    command = ["git", "ls-files"]
    if include_untracked:
        command.extend(["--cached", "--others", "--exclude-standard"])
    if pattern:
        command.extend(["--", pattern])
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening YAML delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing YAML delimiter") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            raise ValueError(f"invalid top-level frontmatter line: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def validate_skills(errors: list[str], public_files: set[str]) -> None:
    data = json.loads(SKILL_INDEX.read_text(encoding="utf-8"))
    skills = data.get("skills", [])
    expected_count = data.get("official_skill_count")
    if expected_count != len(skills):
        errors.append(
            f"skill-index count mismatch: official_skill_count={expected_count}, entries={len(skills)}"
        )
    if data.get("public_skill_count") != expected_count:
        errors.append(
            "skill-index public/official count mismatch: "
            f"public_skill_count={data.get('public_skill_count')}, "
            f"official_skill_count={expected_count}"
        )

    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    if data.get("version") != version or data.get("public_release_version") != version:
        errors.append(
            "version mismatch: "
            f"VERSION={version}, index.version={data.get('version')}, "
            f"index.public_release_version={data.get('public_release_version')}"
        )
    readme = README_FILE.read_text(encoding="utf-8")
    expected_summary = f"当前公开版：**{version}** · 正式入口与 Skills：**{expected_count} 个**"
    if expected_summary not in readme:
        errors.append(f"README missing current release summary: {expected_summary}")

    indexed_paths = {item["path"] for item in skills}
    present_paths = {
        str(Path(name).parent)
        for name in public_files
        if name.endswith("/SKILL.md")
        if len(Path(name).parts) == 2
    }
    if indexed_paths != present_paths:
        errors.append(
            "public Skill folders differ from skill-index: "
            f"only_index={sorted(indexed_paths - present_paths)}, "
            f"only_files={sorted(present_paths - indexed_paths)}"
        )

    for item in skills:
        folder = ROOT / item["path"]
        skill_file = folder / "SKILL.md"
        agent_file = folder / "agents" / "openai.yaml"
        if not skill_file.is_file():
            errors.append(f"missing {skill_file.relative_to(ROOT)}")
            continue
        try:
            metadata = parse_frontmatter(skill_file)
        except ValueError as exc:
            errors.append(f"{skill_file.relative_to(ROOT)}: {exc}")
            continue
        if set(metadata) != {"name", "description"}:
            errors.append(
                f"{skill_file.relative_to(ROOT)} frontmatter keys must be name and description: "
                f"{sorted(metadata)}"
            )
        if metadata.get("name") != item["name"] or item["path"] != item["name"]:
            errors.append(
                f"name mismatch for {item['path']}: index={item['name']}, "
                f"frontmatter={metadata.get('name')}"
            )
        if not agent_file.is_file():
            errors.append(f"missing {agent_file.relative_to(ROOT)}")
        else:
            agent_text = agent_file.read_text(encoding="utf-8")
            for field in ("display_name:", "short_description:", "default_prompt:"):
                if field not in agent_text:
                    errors.append(f"{agent_file.relative_to(ROOT)} missing {field[:-1]}")
            if f"${item['name']}" not in agent_text:
                errors.append(
                    f"{agent_file.relative_to(ROOT)} default_prompt does not reference ${item['name']}"
                )


def validate_links(errors: list[str], tracked: set[str]) -> None:
    for name in sorted(path for path in tracked if path.endswith(".md")):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split()[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            try:
                relative = str(resolved.relative_to(ROOT))
            except ValueError:
                errors.append(f"{name}: link escapes repository: {target}")
                continue
            if relative not in tracked:
                errors.append(f"{name}: link target is not tracked: {target}")


def validate_sensitive_text(errors: list[str], tracked: set[str]) -> None:
    text_suffixes = {".md", ".json", ".yaml", ".yml", ".py", ".txt"}
    for name in sorted(tracked):
        path = ROOT / name
        if path.suffix.lower() not in text_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{name}: detected {label}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--working-tree",
        action="store_true",
        help="Include untracked, non-ignored release-candidate files for pre-commit validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    public_files = set(git_files(include_untracked=args.working_tree))
    validate_skills(errors, public_files)
    validate_links(errors, public_files)
    validate_sensitive_text(errors, public_files)

    if errors:
        print("Public repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    data = json.loads(SKILL_INDEX.read_text(encoding="utf-8"))
    print(
        f"Public repository valid: {data['official_skill_count']} Skills, "
        f"version {data['version']}, {len(public_files)} "
        f"{'working-tree' if args.working_tree else 'tracked'} files checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
