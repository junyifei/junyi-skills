#!/usr/bin/env python3
"""Preview or safely apply a knowledge-base creation/write manifest."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


ALLOWED_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".yaml", ".yml"}


def within_root(root: Path, target: Path) -> bool:
    try:
        return os.path.commonpath([str(root), str(target)]) == str(root)
    except ValueError:
        return False


def safe_target(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if not relative.strip() or rel.is_absolute() or ".." in rel.parts or rel == Path("."):
        raise ValueError(f"unsafe relative path: {relative!r}")
    target = (root / rel).resolve(strict=False)
    if not within_root(root, target):
        raise ValueError(f"path escapes vault root: {relative!r}")
    return target


def suffixed_path(path: Path) -> Path:
    for number in range(2, 10000):
        candidate = path.with_name(f"{path.stem}-{number}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"cannot find a free suffixed name for {path}")


def load_content(entry: dict, manifest_dir: Path) -> str:
    has_inline = "content" in entry
    has_file = "content_file" in entry
    if has_inline == has_file:
        raise ValueError("file entry must contain exactly one of content or content_file")
    if has_inline:
        if not isinstance(entry["content"], str):
            raise ValueError("file content must be a string")
        return entry["content"]
    source = Path(entry["content_file"])
    if not source.is_absolute():
        source = manifest_dir / source
    return source.read_text(encoding="utf-8")


def prepare(manifest_path: Path, root: Path, conflict: str) -> list[dict]:
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("manifest root must be a JSON list")

    root = root.expanduser().resolve(strict=False)
    prepared: list[dict] = []
    planned_dirs = {root}
    seen_targets: set[Path] = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"entry {index} must be an object")
        kind = entry.get("type")
        if kind not in {"directory", "file"}:
            raise ValueError(f"entry {index} has unsupported type: {kind}")
        target = safe_target(root, str(entry.get("path", "")))
        if target in seen_targets:
            raise ValueError(f"duplicate manifest target: {target}")
        seen_targets.add(target)

        if kind == "directory":
            if target.exists() and not target.is_dir():
                raise FileExistsError(f"directory target is an existing file: {target}")
            planned_dirs.add(target)
            prepared.append({"type": kind, "target": target, "action": "keep" if target.is_dir() else "create"})
            continue

        if target.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError(f"file extension not allowed: {target.suffix}")
        content = load_content(entry, manifest_path.parent)
        actual_target = target
        action = "create"
        if target.exists():
            if target.is_dir():
                raise IsADirectoryError(f"file target is an existing directory: {target}")
            if conflict == "error":
                raise FileExistsError(f"file already exists: {target}")
            if conflict == "suffix":
                actual_target = suffixed_path(target)
                action = "create-with-suffix"
            else:
                action = "overwrite"

        parent = actual_target.parent
        if not parent.is_dir() and parent not in planned_dirs:
            raise FileNotFoundError(
                f"parent directory is not present or explicitly planned: {parent}"
            )
        prepared.append(
            {"type": kind, "target": actual_target, "action": action, "content": content}
        )
    overwrite_count = sum(item.get("action") == "overwrite" for item in prepared)
    if overwrite_count > 1:
        raise ValueError(
            "one manifest may overwrite at most one file; split overwrite operations into separately reviewed batches"
        )
    return prepared


def atomic_write(path: Path, content: str, overwrite: bool) -> None:
    if not path.parent.is_dir():
        raise FileNotFoundError(f"parent directory does not exist: {path.parent}")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for start in range(0, len(content), 20000):
                handle.write(content[start : start + 20000])
            handle.flush()
            os.fsync(handle.fileno())
        if overwrite:
            os.replace(temp_path, path)
        else:
            os.link(temp_path, path)
            temp_path.unlink()
    finally:
        if temp_path.exists():
            temp_path.unlink()


def apply(prepared: list[dict], root: Path) -> None:
    root = root.expanduser().resolve(strict=False)
    created_files: list[Path] = []
    created_dirs: list[Path] = []
    root_existed = root.exists()
    try:
        if not root_existed:
            root.mkdir(parents=True)
            created_dirs.append(root)
        directories = sorted(
            (item for item in prepared if item["type"] == "directory"),
            key=lambda item: len(item["target"].parts),
        )
        files = [
            item for item in prepared if item["type"] == "file" and item["action"] != "overwrite"
        ]
        files.extend(
            item for item in prepared if item["type"] == "file" and item["action"] == "overwrite"
        )
        for item in [*directories, *files]:
            target = item["target"]
            if item["type"] == "directory":
                if not target.exists():
                    target.mkdir()
                    created_dirs.append(target)
            else:
                atomic_write(target, item["content"], overwrite=item["action"] == "overwrite")
                if item["action"] != "overwrite":
                    created_files.append(target)
    except Exception:
        for path in reversed(created_files):
            if path.is_file():
                path.unlink()
        for path in sorted(created_dirs, key=lambda p: len(p.parts), reverse=True):
            try:
                path.rmdir()
            except OSError:
                pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Apply after a reviewed dry run")
    parser.add_argument("--conflict", choices=("error", "suffix", "overwrite"), default="error")
    args = parser.parse_args()
    try:
        prepared = prepare(args.manifest, args.root, args.conflict)
        print("APPLY" if args.apply else "DRY RUN")
        for item in prepared:
            print(f"- {item['action']}: {item['target']}")
        if args.apply:
            apply(prepared, args.root)
            print(f"Applied {len(prepared)} operations")
        else:
            print("No files changed. Re-run with --apply only after reviewing this plan.")
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
