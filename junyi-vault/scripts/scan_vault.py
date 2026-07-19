#!/usr/bin/env python3
"""Read-only structural scan for a Markdown/Obsidian-style knowledge base."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_IGNORES = {".git", ".obsidian", ".trash", ".DS_Store", "node_modules", "__pycache__"}
GENERIC_NAMES = {"其他", "其它", "杂项", "临时", "未分类", "misc", "other", "temp", "inbox"}


def normalized_name(name: str) -> str:
    return re.sub(r"[\s_\-—.]+", "", name).casefold()


def scan(root: Path, max_depth: int = 6) -> dict:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"vault root is not a directory: {root}")

    files: list[str] = []
    directories: list[str] = []
    symlinks: list[str] = []
    empty_dirs: list[str] = []
    ignored: list[str] = []
    depth_counts: Counter[int] = Counter()
    names: defaultdict[str, list[str]] = defaultdict(list)

    for current, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        rel_current = current_path.relative_to(root)
        depth = len(rel_current.parts)

        kept_dirs = []
        for dirname in sorted(dirnames):
            child = current_path / dirname
            rel = child.relative_to(root).as_posix()
            if dirname in DEFAULT_IGNORES:
                ignored.append(rel)
            elif child.is_symlink():
                symlinks.append(rel)
            elif depth + 1 > max_depth:
                ignored.append(rel + " (depth limit)")
            else:
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        visible_files = []
        for filename in sorted(filenames):
            child = current_path / filename
            rel = child.relative_to(root).as_posix()
            if filename in DEFAULT_IGNORES:
                ignored.append(rel)
            elif child.is_symlink():
                symlinks.append(rel)
            else:
                visible_files.append(rel)
                files.append(rel)
                depth_counts[len(Path(rel).parts) - 1] += 1

        if depth > 0:
            rel_dir = rel_current.as_posix()
            directories.append(rel_dir)
            names[normalized_name(current_path.name)].append(rel_dir)
            if not kept_dirs and not visible_files:
                empty_dirs.append(rel_dir)

    root_files = [path for path in files if len(Path(path).parts) == 1]
    deep_files = [path for path in files if len(Path(path).parts) > 3]
    generic_dirs = [
        path for path in directories if normalized_name(Path(path).name) in {normalized_name(n) for n in GENERIC_NAMES}
    ]
    duplicate_names = {key: value for key, value in names.items() if key and len(value) > 1}

    first_level = sorted(path for path in directories if len(Path(path).parts) == 1)
    second_level = sorted(path for path in directories if len(Path(path).parts) == 2)

    return {
        "root": str(root),
        "summary": {
            "files": len(files),
            "directories": len(directories),
            "root_files": len(root_files),
            "empty_directories": len(empty_dirs),
            "deep_files": len(deep_files),
            "symlinks": len(symlinks),
        },
        "structure": {"domains": first_level, "classes": second_level},
        "signals": {
            "root_files": root_files,
            "empty_directories": empty_dirs,
            "deep_files": deep_files,
            "generic_directories": generic_dirs,
            "duplicate_normalized_directory_names": duplicate_names,
            "symlinks_not_followed": symlinks,
        },
        "file_depth_counts": {str(key): value for key, value in sorted(depth_counts.items())},
        "ignored": ignored,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--output", type=Path, help="Optional JSON output file")
    args = parser.parse_args()
    try:
        report = scan(args.root, args.max_depth)
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            print(payload, end="")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
