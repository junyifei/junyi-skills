#!/usr/bin/env python3
"""Split a long learning source at headings/paragraphs with a hard character cap."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


BOUNDARY_RE = re.compile(r"^(?:#{1,6}\s+|第[一二三四五六七八九十百\d]+[章节部分]|\d+(?:\.\d+)*[、.\s])")


def natural_units(text: str) -> list[str]:
    lines = text.splitlines(keepends=True)
    units: list[str] = []
    current: list[str] = []
    for line in lines:
        starts_boundary = BOUNDARY_RE.match(line.strip()) or (not line.strip() and current)
        if starts_boundary and current:
            units.append("".join(current))
            current = []
        current.append(line)
    if current:
        units.append("".join(current))
    return [unit for unit in units if unit.strip()]


def hard_pieces(unit: str, max_chars: int) -> list[str]:
    if len(unit) <= max_chars:
        return [unit]
    return [unit[index : index + max_chars] for index in range(0, len(unit), max_chars)]


def split_text(text: str, max_chars: int) -> list[str]:
    if max_chars < 500:
        raise ValueError("max_chars must be at least 500")
    chunks: list[str] = []
    current = ""
    for unit in natural_units(text):
        for piece in hard_pieces(unit, max_chars):
            if current and len(current) + len(piece) > max_chars:
                chunks.append(current.strip())
                current = ""
            current += piece
            if len(current) >= max_chars:
                chunks.append(current.strip())
                current = ""
    if current.strip():
        chunks.append(current.strip())
    return chunks


def ensure_fresh(out_dir: Path) -> None:
    if out_dir.exists() and (list(out_dir.glob("chunk_*.md")) or (out_dir / "manifest.json").exists()):
        raise FileExistsError("output already contains chunks; resume it or choose a fresh directory")


def build_manifest(source: Path, out_dir: Path, chunks: list[str], max_chars: int) -> dict:
    entries = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_path = (out_dir / f"chunk_{index:03d}.md").resolve()
        ledger_path = (out_dir.parent / "ledgers" / f"chunk_{index:03d}.ledger.md").resolve()
        entries.append(
            {
                "chunk": index,
                "path": str(chunk_path),
                "chars": len(chunk),
                "status": "pending",
                "skip_reason": "",
                "ledger_path": str(ledger_path),
            }
        )
    return {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source.resolve()),
        "source_bytes": source.stat().st_size,
        "max_chars": max_chars,
        "chunk_count": len(chunks),
        "chunks": entries,
        "final_path": "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-chars", type=int, default=8000)
    args = parser.parse_args()

    try:
        if not args.input.is_file():
            raise FileNotFoundError(f"input not found: {args.input}")
        ensure_fresh(args.out_dir)
        text = args.input.read_text(encoding="utf-8")
        chunks = split_text(text, args.max_chars)
        if not chunks:
            raise ValueError("input contains no readable content")
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir.parent / "ledgers").mkdir(parents=True, exist_ok=True)
        manifest = build_manifest(args.input, args.out_dir, chunks, args.max_chars)
        for entry, chunk in zip(manifest["chunks"], chunks):
            Path(entry["path"]).write_text(
                f"# Source chunk {entry['chunk']:03d}\n\n{chunk}\n", encoding="utf-8"
            )
        manifest_path = args.out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(chunks)} chunks to {args.out_dir}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
