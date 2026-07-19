#!/usr/bin/env python3
"""Regression tests for vault scanning and manifest application."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_manifest as manifest_tool  # noqa: E402
import scan_vault  # noqa: E402


PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"PASS {name}")
    else:
        FAIL += 1
        print(f"FAIL {name}: {detail}")


def write_manifest(path: Path, entries: list[dict]) -> None:
    path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")


def test_dry_run_and_apply() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "vault"
        manifest = Path(directory) / "plan.json"
        entries = [
            {"type": "directory", "path": "创作"},
            {"type": "directory", "path": "创作/素材"},
            {"type": "file", "path": "索引.md", "content": "# 索引\n"},
            {"type": "file", "path": "创作/素材/第一条.md", "content": "# 第一条\n"},
        ]
        write_manifest(manifest, entries)
        prepared = manifest_tool.prepare(manifest, root, "error")
        check("prepare does not create root", not root.exists())
        manifest_tool.apply(prepared, root)
        check("apply creates planned file", (root / "创作/素材/第一条.md").is_file())
        check("apply preserves UTF-8", (root / "索引.md").read_text(encoding="utf-8") == "# 索引\n")


def test_directory_order_is_safe() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "vault"
        manifest = Path(directory) / "plan.json"
        entries = [
            {"type": "directory", "path": "父/子"},
            {"type": "directory", "path": "父"},
            {"type": "file", "path": "父/子/笔记.md", "content": "ok"},
        ]
        write_manifest(manifest, entries)
        prepared = manifest_tool.prepare(manifest, root, "error")
        manifest_tool.apply(prepared, root)
        check("directory application is independent of manifest order", (root / "父/子/笔记.md").is_file())


def test_conflicts_and_suffix() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "vault"
        root.mkdir()
        existing = root / "笔记.md"
        existing.write_text("old", encoding="utf-8")
        manifest = Path(directory) / "plan.json"
        write_manifest(manifest, [{"type": "file", "path": "笔记.md", "content": "new"}])
        try:
            manifest_tool.prepare(manifest, root, "error")
            conflict_failed = False
        except FileExistsError:
            conflict_failed = True
        check("default conflict policy refuses overwrite", conflict_failed)
        prepared = manifest_tool.prepare(manifest, root, "suffix")
        check("suffix policy previews changed target", prepared[0]["target"].name == "笔记-2.md")
        manifest_tool.apply(prepared, root)
        check("suffix policy preserves original", existing.read_text(encoding="utf-8") == "old")


def test_multiple_overwrites_require_separate_batches() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "vault"
        root.mkdir()
        (root / "a.md").write_text("a", encoding="utf-8")
        (root / "b.md").write_text("b", encoding="utf-8")
        manifest = Path(directory) / "plan.json"
        write_manifest(
            manifest,
            [
                {"type": "file", "path": "a.md", "content": "new a"},
                {"type": "file", "path": "b.md", "content": "new b"},
            ],
        )
        try:
            manifest_tool.prepare(manifest, root, "overwrite")
            rejected = False
        except ValueError:
            rejected = True
        check("multiple overwrites require separate review batches", rejected)


def test_path_escape_and_all_or_nothing_validation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "vault"
        root.mkdir()
        manifest = Path(directory) / "plan.json"
        write_manifest(
            manifest,
            [
                {"type": "file", "path": "safe.md", "content": "safe"},
                {"type": "file", "path": "../escape.md", "content": "bad"},
            ],
        )
        try:
            manifest_tool.prepare(manifest, root, "error")
            rejected = False
        except ValueError:
            rejected = True
        check("path traversal is rejected", rejected)
        check("failed prevalidation writes nothing", not (root / "safe.md").exists())


def test_symlink_escape() -> None:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        root = base / "vault"
        outside = base / "outside"
        root.mkdir()
        outside.mkdir()
        (root / "link").symlink_to(outside, target_is_directory=True)
        manifest = base / "plan.json"
        write_manifest(manifest, [{"type": "file", "path": "link/escape.md", "content": "bad"}])
        try:
            manifest_tool.prepare(manifest, root, "error")
            rejected = False
        except ValueError:
            rejected = True
        check("symlink escape is rejected", rejected)


def test_scan_signals() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "vault"
        (root / "创作/素材/旧/更深").mkdir(parents=True)
        (root / "创作/其他").mkdir(parents=True)
        (root / "工作/素材").mkdir(parents=True)
        (root / "散落.md").write_text("root", encoding="utf-8")
        (root / "创作/素材/旧/更深/笔记.md").write_text("deep", encoding="utf-8")
        report = scan_vault.scan(root)
        signals = report["signals"]
        check("scan detects root files", "散落.md" in signals["root_files"], str(signals))
        check("scan detects deep files", bool(signals["deep_files"]), str(signals))
        check("scan detects generic directory", "创作/其他" in signals["generic_directories"], str(signals))
        duplicates = signals["duplicate_normalized_directory_names"]
        check("scan detects duplicate class names", any(len(paths) == 2 for paths in duplicates.values()), str(duplicates))


def main() -> int:
    test_dry_run_and_apply()
    test_directory_order_is_safe()
    test_conflicts_and_suffix()
    test_multiple_overwrites_require_separate_batches()
    test_path_escape_and_all_or_nothing_validation()
    test_symlink_escape()
    test_scan_signals()
    print(f"RESULT {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
