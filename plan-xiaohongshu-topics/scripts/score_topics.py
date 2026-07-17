#!/usr/bin/env python3
"""Validate Xiaohongshu topic scorecards without replacing analyst judgment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DIMENSIONS = {
    "user_demand": 15,
    "search_save": 10,
    "creator_proof": 15,
    "strategic_fit": 15,
    "novel_angle": 10,
    "series_potential": 8,
    "audience_precision": 10,
    "integrity": 7,
    "validation_clarity": 5,
    "metric_match": 5,
}
GATES = {
    "qualification",
    "audience_fit",
    "reality_proof",
    "strategic_fit",
    "distinctness",
    "integrity",
}
GATE_VALUES = {"pass", "repairable_fail", "fail"}
DECISIONS = {"keep", "rewrite", "observe", "eliminate"}
DISTRIBUTION_POLICIES = {"strict_shareability", "task_calibrated"}
DISTRIBUTION_GATES = {"counterintuitive", "shared_scene", "forwarding_job"}
CONTENT_TASKS = {"attention", "trust", "commercial"}


def numeric_band(total: int) -> str:
    if total >= 80:
        return "strong"
    if total >= 65:
        return "conditional"
    return "weak"


def validate_topic(topic: dict) -> tuple[dict, list[str]]:
    errors: list[str] = []
    topic_id = topic.get("topic_id", "<missing>")
    scores = topic.get("scores")
    if not isinstance(scores, dict):
        return topic, [f"{topic_id}: scores must be an object"]

    missing_scores = set(DIMENSIONS) - set(scores)
    extra_scores = set(scores) - set(DIMENSIONS)
    if missing_scores:
        errors.append(f"{topic_id}: missing score dimensions {sorted(missing_scores)}")
    if extra_scores:
        errors.append(f"{topic_id}: unknown score dimensions {sorted(extra_scores)}")

    total = 0
    for name, maximum in DIMENSIONS.items():
        value = scores.get(name)
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{topic_id}: {name} must be an integer")
            continue
        if value < 0 or value > maximum:
            errors.append(f"{topic_id}: {name}={value} outside 0..{maximum}")
            continue
        total += value

    gates = topic.get("gates")
    if not isinstance(gates, dict):
        errors.append(f"{topic_id}: gates must be an object")
        gates = {}
    missing_gates = GATES - set(gates)
    extra_gates = set(gates) - GATES
    if missing_gates:
        errors.append(f"{topic_id}: missing gates {sorted(missing_gates)}")
    if extra_gates:
        errors.append(f"{topic_id}: unknown gates {sorted(extra_gates)}")
    for name, value in gates.items():
        if value not in GATE_VALUES:
            errors.append(f"{topic_id}: gate {name} has invalid value {value!r}")

    decision = topic.get("analyst_decision")
    distribution_policy = topic.get("distribution_policy")
    distribution_gates = topic.get("distribution_gates")
    distribution_failed: list[str] = []
    distribution_repairable: list[str] = []
    if distribution_policy is not None or distribution_gates is not None:
        if distribution_policy not in DISTRIBUTION_POLICIES:
            errors.append(
                f"{topic_id}: distribution_policy must be one of {sorted(DISTRIBUTION_POLICIES)}"
            )
        if not isinstance(distribution_gates, dict):
            errors.append(f"{topic_id}: distribution_gates must be an object")
            distribution_gates = {}
        missing_distribution = DISTRIBUTION_GATES - set(distribution_gates)
        extra_distribution = set(distribution_gates) - DISTRIBUTION_GATES
        if missing_distribution:
            errors.append(
                f"{topic_id}: missing distribution gates {sorted(missing_distribution)}"
            )
        if extra_distribution:
            errors.append(
                f"{topic_id}: unknown distribution gates {sorted(extra_distribution)}"
            )
        distribution_results: dict[str, str | None] = {}
        for name, value in distribution_gates.items():
            result = value.get("result") if isinstance(value, dict) else value
            distribution_results[name] = result
            if result not in GATE_VALUES:
                errors.append(
                    f"{topic_id}: distribution gate {name} has invalid result {result!r}"
                )
        distribution_failed = [
            name for name, value in distribution_results.items() if value == "fail"
        ]
        distribution_repairable = [
            name for name, value in distribution_results.items() if value == "repairable_fail"
        ]

        content_task = topic.get("primary_content_task")
        if content_task not in CONTENT_TASKS:
            errors.append(
                f"{topic_id}: primary_content_task must be one of {sorted(CONTENT_TASKS)} when distribution gates are used"
            )
        distribution_blocks_keep = distribution_policy == "strict_shareability" or content_task == "attention"
        if decision == "keep" and distribution_blocks_keep and (
            distribution_failed or distribution_repairable
        ):
            errors.append(
                f"{topic_id}: {distribution_policy or 'attention'} keep requires every distribution gate to pass"
            )
        if (
            decision == "keep"
            and distribution_policy == "task_calibrated"
            and content_task in {"trust", "commercial"}
            and (distribution_failed or distribution_repairable)
            and not topic.get("narrow_role_basis")
        ):
            errors.append(
                f"{topic_id}: narrow trust/commercial keep requires narrow_role_basis when a distribution gate does not pass"
            )

    if decision not in DECISIONS:
        errors.append(f"{topic_id}: analyst_decision must be one of {sorted(DECISIONS)}")
    if not topic.get("decision_basis"):
        errors.append(f"{topic_id}: decision_basis is required")

    failed = [name for name, value in gates.items() if value == "fail"]
    repairable = [name for name, value in gates.items() if value == "repairable_fail"]
    if decision == "keep" and (failed or repairable):
        errors.append(f"{topic_id}: keep requires every gate to pass")
    if decision == "keep" and total < 80 and not topic.get("exception_basis"):
        errors.append(f"{topic_id}: keep below 80 requires an explicit exception; use rewrite/observe otherwise")
    if failed and decision not in {"eliminate"} and not topic.get("exception_basis"):
        errors.append(f"{topic_id}: failed gates {failed} normally require eliminate or exception_basis")
    if decision == "rewrite" and not topic.get("rewrite_direction"):
        errors.append(f"{topic_id}: rewrite_direction is required for rewrite")
    if decision == "observe" and not topic.get("unlock_condition"):
        errors.append(f"{topic_id}: unlock_condition is required for observe")

    enriched = dict(topic)
    enriched["total"] = total
    enriched["numeric_band"] = numeric_band(total)
    enriched["gate_summary"] = {
        "failed": failed,
        "repairable_fail": repairable,
        "all_pass": not failed and not repairable,
    }
    if distribution_policy is not None or distribution_gates is not None:
        enriched["distribution_gate_summary"] = {
            "failed": distribution_failed,
            "repairable_fail": distribution_repairable,
            "all_pass": not distribution_failed and not distribution_repairable,
            "policy": distribution_policy,
        }
    return enriched, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate without writing output")
    args = parser.parse_args()

    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    topics = payload.get("topics") if isinstance(payload, dict) else None
    if not isinstance(topics, list):
        print("ERROR: top-level topics must be an array", file=sys.stderr)
        return 2

    enriched_topics = []
    errors: list[str] = []
    for topic in topics:
        if not isinstance(topic, dict):
            errors.append("topic item must be an object")
            continue
        enriched, topic_errors = validate_topic(topic)
        enriched_topics.append(enriched)
        errors.extend(topic_errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    result = dict(payload)
    result["topics"] = enriched_topics
    result["summary"] = {
        decision: sum(1 for topic in enriched_topics if topic["analyst_decision"] == decision)
        for decision in sorted(DECISIONS)
    }

    if args.output and not args.check:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
