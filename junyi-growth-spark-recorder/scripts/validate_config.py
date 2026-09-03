#!/usr/bin/env python3
"""Validate a private configuration for junyi-growth-spark-recorder."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    print(f"INVALID: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate_config.py <config.json>")

    path = Path(sys.argv[1]).expanduser()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail("config file does not exist")
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON: {exc}")

    if data.get("schema_version") != 1:
        fail("schema_version must be 1")

    root = data.get("archive_root")
    if not isinstance(root, str) or not root.strip():
        fail("archive_root is required")
    archive_root = Path(root).expanduser()
    if not archive_root.is_absolute():
        fail("archive_root must be an absolute path")

    subjects = data.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        fail("subjects must contain at least one item")

    ids: set[str] = set()
    names: set[str] = set()
    for number, subject in enumerate(subjects, start=1):
        if not isinstance(subject, dict):
            fail(f"subjects[{number}] must be an object")
        subject_id = subject.get("id")
        name = subject.get("display_name")
        if not isinstance(subject_id, str) or not ID_RE.fullmatch(subject_id):
            fail(f"subjects[{number}].id must use lowercase letters, digits and hyphens")
        if not isinstance(name, str) or not name.strip():
            fail(f"subjects[{number}].display_name is required")
        if subject_id in ids:
            fail(f"duplicate subject id: {subject_id}")
        if name in names:
            fail(f"duplicate display_name: {name}")
        ids.add(subject_id)
        names.add(name)
        birth_date = subject.get("birth_date", "")
        if birth_date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", birth_date):
            fail(f"subjects[{number}].birth_date must be YYYY-MM-DD or empty")

    policy = data.get("write_policy")
    if not isinstance(policy, dict):
        fail("write_policy is required")
    if policy.get("event_records") is not True:
        fail("write_policy.event_records must be true")
    if policy.get("profile_updates_require_separate_confirmation") is not True:
        fail("profile updates must require separate confirmation")

    print(f"VALID: {len(subjects)} subject(s); archive_root={archive_root}")


if __name__ == "__main__":
    main()
