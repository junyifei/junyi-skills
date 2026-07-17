#!/usr/bin/env python3
"""Validate and score personal-IP positioning candidates from a JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


WEIGHTS = {
    "trigger_strength": 15,
    "asset_ownership": 10,
    "content_fuel": 10,
    "retell_clarity": 10,
    "attention_evidence": 10,
    "ability_proof": 15,
    "payment_adjacency": 15,
    "scale_ceiling": 10,
    "ethical_fit": 5,
}

GATES = (
    "recall_situation",
    "content_fuel_100",
    "retell_sentence",
    "ability_trust",
    "payment_test",
    "ethical_fit",
)

STATUSES = {"pass", "provisional", "fail", "unknown"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score candidates after checking the six must-pass basics."
    )
    parser.add_argument("input", type=Path, help="JSON file containing a candidates array")
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="Output format"
    )
    parser.add_argument("--output", type=Path, help="Optional output file; stdout when omitted")
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("candidates"), list):
        raise ValueError("top level must be an object with a candidates array")
    if not payload["candidates"]:
        raise ValueError("candidates array cannot be empty")
    return payload


def outcome_for(gates: dict) -> str:
    values = set(gates.values())
    if "fail" in values:
        return "reject"
    if "unknown" in values:
        return "needs evidence"
    if "provisional" in values:
        return "provisional"
    return "eligible"


def validate_candidate(raw: dict, index: int) -> tuple[dict, list[str]]:
    errors: list[str] = []
    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"candidate {index}: name must be a non-empty string")
        name = f"candidate-{index}"

    gates = raw.get("gates")
    if not isinstance(gates, dict):
        errors.append(f"{name}: gates must be an object")
        gates = {}
    clean_gates = {}
    for key in GATES:
        value = gates.get(key)
        if value not in STATUSES:
            errors.append(
                f"{name}: gate {key} must be one of {sorted(STATUSES)}, got {value!r}"
            )
        else:
            clean_gates[key] = value

    scores = raw.get("scores")
    if not isinstance(scores, dict):
        errors.append(f"{name}: scores must be an object")
        scores = {}
    clean_scores = {}
    for key in WEIGHTS:
        value = scores.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{name}: score {key} must be a number from 0 to 5")
            continue
        if not 0 <= float(value) <= 5:
            errors.append(f"{name}: score {key}={value} is outside 0-5")
            continue
        clean_scores[key] = float(value)

    evidence = raw.get("evidence", [])
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        errors.append(f"{name}: evidence must be an array of evidence IDs or notes")
        evidence = []

    if errors:
        return {}, errors

    total = round(sum(clean_scores[key] / 5 * WEIGHTS[key] for key in WEIGHTS), 1)
    return {
        "name": name.strip(),
        "gates": clean_gates,
        "outcome": outcome_for(clean_gates),
        "score": total,
        "scores": clean_scores,
        "evidence": evidence,
        "evidence_warning": not evidence,
    }, []


def to_markdown(results: list[dict]) -> str:
    lines = [
        "| Candidate | Basics result | Weighted score | Evidence |",
        "|---|---|---:|---|",
    ]
    for item in sorted(results, key=lambda row: row["score"], reverse=True):
        evidence = ", ".join(item["evidence"]) if item["evidence"] else "MISSING"
        lines.append(
            f'| {item["name"]} | {item["outcome"]} | {item["score"]:.1f} | {evidence} |'
        )
    lines.append("")
    lines.append("Scores compare candidates; they do not override a failed basic check or prove payment.")
    if any(item["evidence_warning"] for item in results):
        lines.append("WARNING: at least one candidate has no evidence IDs or notes.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args.input)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    results = []
    errors = []
    for index, raw in enumerate(payload["candidates"], start=1):
        if not isinstance(raw, dict):
            errors.append(f"candidate {index}: must be an object")
            continue
        result, item_errors = validate_candidate(raw, index)
        results.append(result) if result else None
        errors.extend(item_errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    output = (
        json.dumps({"candidates": results, "weights": WEIGHTS}, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else to_markdown(results)
    )
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
