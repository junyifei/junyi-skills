#!/usr/bin/env python3
"""Split a transcript into bounded Markdown chunks and create a resume manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


BOUNDARY_RE = re.compile(
    r"^(?:#{1,6}\s+|(?:说话人\s*\d+|speaker\s*\d+|[^\s]{1,24})\s+"
    r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?::\d{2})?\s*$)",
    re.IGNORECASE,
)


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", path.stem).strip("_")
    return stem or "transcript"


def split_oversized_line(line: str, max_chars: int) -> list[str]:
    """Hard-split a line that alone exceeds the limit."""
    if len(line) <= max_chars:
        return [line]
    ending = "\n" if line.endswith("\n") else ""
    body = line[:-1] if ending else line
    pieces = [body[i : i + max_chars] for i in range(0, len(body), max_chars)]
    return [piece + ("\n" if i < len(pieces) - 1 or ending else "") for i, piece in enumerate(pieces)]


def group_units(lines: list[str]) -> list[str]:
    """Keep a speaker/timestamp label with the utterance lines that follow it."""
    units: list[str] = []
    current: list[str] = []
    for line in lines:
        if BOUNDARY_RE.match(line.strip()) and current:
            units.append("".join(current))
            current = []
        current.append(line)
    if current:
        units.append("".join(current))
    return units


def bounded_units(lines: list[str], max_chars: int) -> list[str]:
    result: list[str] = []
    for unit in group_units(lines):
        if len(unit) <= max_chars:
            result.append(unit)
            continue
        pieces: list[str] = []
        for line in unit.splitlines(keepends=True):
            pieces.extend(split_oversized_line(line, max_chars))
        current = ""
        for piece in pieces:
            if current and len(current) + len(piece) > max_chars:
                result.append(current)
                current = ""
            current += piece
        if current:
            result.append(current)
    return result


def finalize_chunk(parts: list[str], max_chars: int) -> str:
    body = "".join(parts).strip()
    if len(body) < max_chars:
        return body + "\n"
    return body


def split_lines(lines: list[str], max_chars: int) -> list[str]:
    if max_chars < 500:
        raise ValueError("max_chars must be at least 500")

    chunks: list[str] = []
    current: list[str] = []
    current_size = 0

    for unit in bounded_units(lines, max_chars):
        unit_size = len(unit)
        if current and current_size + unit_size > max_chars:
            chunks.append(finalize_chunk(current, max_chars))
            current, current_size = [], 0
        current.append(unit)
        current_size += unit_size
        if current_size >= max_chars:
            chunks.append(finalize_chunk(current, max_chars))
            current, current_size = [], 0

    if current:
        chunks.append(finalize_chunk(current, max_chars))

    return [chunk for chunk in chunks if chunk.strip()]


def ensure_fresh_output(out_dir: Path) -> None:
    if not out_dir.exists():
        return
    generated = list(out_dir.glob("chunk_*.md")) + list(out_dir.glob("manifest.json"))
    if generated:
        names = ", ".join(path.name for path in generated[:5])
        raise FileExistsError(
            f"output directory already contains generated files ({names}); "
            "resume from its manifest or choose a fresh directory"
        )


def build_manifest(source: Path, out_dir: Path, chunks: list[str], max_chars: int) -> dict:
    isolation_required = len(chunks) >= 3
    entries = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_path = (out_dir / f"chunk_{index:03d}.md").resolve()
        entries.append(
            {
                "chunk": index,
                "path": str(chunk_path),
                "chars": len(chunk),
                "status": "pending",
                "skip_reason": "",
                "distilled_path": str(chunk_path.with_suffix(".distilled.md")),
                "worker_mode": "unassigned" if isolation_required else "not-required",
                "worker_run": "",
            }
        )
    return {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source.resolve()),
        "source_bytes": source.stat().st_size,
        "out_dir": str(out_dir.resolve()),
        "max_chars": max_chars,
        "chunk_count": len(chunks),
        "workflow_status": (
            "prepared_for_isolated_processing" if isolation_required else "prepared"
        ),
        "isolation": {
            "required": isolation_required,
            "threshold": 3,
            "mode": "unassigned" if isolation_required else "not-required",
            "orchestrator_read_raw_chunks": False,
        },
        "chunks": entries,
        "final_path": "",
        "validation": {"status": "pending", "checked_at": "", "errors": []},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 transcript in Markdown or text")
    parser.add_argument("--out-dir", type=Path, required=True, help="Fresh output directory")
    parser.add_argument("--max-chars", type=int, default=8000, help="Hard body limit per chunk")
    args = parser.parse_args()

    try:
        if not args.input.is_file():
            raise FileNotFoundError(f"input not found: {args.input}")
        ensure_fresh_output(args.out_dir)
        text = args.input.read_text(encoding="utf-8")
        chunks = split_lines(text.splitlines(keepends=True), args.max_chars)
        if not chunks:
            raise ValueError("input contains no non-whitespace content")

        args.out_dir.mkdir(parents=True, exist_ok=True)
        stem = safe_stem(args.input)
        manifest = build_manifest(args.input, args.out_dir, chunks, args.max_chars)

        for entry, chunk in zip(manifest["chunks"], chunks):
            chunk_path = Path(entry["path"])
            header = f"# {stem} / chunk {entry['chunk']:03d}\n\n"
            chunk_path.write_text(header + chunk, encoding="utf-8")

        manifest_path = args.out_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(chunks)} chunks to {args.out_dir}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
