#!/usr/bin/env python3
"""Score Xiaohongshu benchmark candidates from a JSON list."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


WEIGHTS = {
    "audience_problem_fit": 20,
    "position_clarity": 10,
    "content_system_overlap": 10,
    "recent_attention": 15,
    "repeatability": 10,
    "operational_replicability": 15,
    "trust_proof": 10,
    "commercial_path_fit": 10,
}

TIER_WEIGHTS = {
    "large": {
        "blockbuster_families": 20,
        "cultural_scale_ceiling": 20,
        "ip_trust_architecture": 20,
        "monetization_visibility": 20,
        "transferable_structure": 20,
    },
    "medium": {
        "recurring_topic_system": 25,
        "serial_formats_cadence": 20,
        "stable_performance": 20,
        "operational_comparability": 20,
        "content_offer_alignment": 15,
    },
    "small": {
        "recent_breakout": 25,
        "lift_over_baseline": 20,
        "multiple_supporting_posts": 20,
        "low_resource_reproducibility": 20,
        "emerging_audience_language": 15,
    },
}

TEMPERAMENT_WEIGHTS = {
    "expression_style": 20,
    "emotional_energy": 20,
    "values_decision_style": 20,
    "lifestyle_texture": 20,
    "narrative_stance": 20,
}


def score(candidate: dict) -> dict:
    values = candidate.get("scores", {})
    missing = [key for key in WEIGHTS if key not in values]
    if missing:
        raise ValueError(f"{candidate.get('name', '<unnamed>')}: missing scores {missing}")

    for key, value in values.items():
        if key in WEIGHTS and (not isinstance(value, (int, float)) or not 0 <= value <= 5):
            raise ValueError(f"{candidate.get('name', '<unnamed>')}: {key} must be 0..5")

    role_scope = candidate.get("role_scope", "core")
    if role_scope not in {"core", "specialist", "post_specimen"}:
        raise ValueError(
            f"{candidate.get('name', '<unnamed>')}: role_scope must be core, specialist, or post_specimen"
        )

    effective_values = dict(values)
    score_adjustments = []
    if candidate.get("one_post_outlier"):
        for key in ("recent_attention", "repeatability"):
            if effective_values[key] > 2:
                effective_values[key] = 2
                score_adjustments.append(f"{key} capped at 2 for one-post outlier")
        if role_scope != "post_specimen":
            raise ValueError(
                f"{candidate.get('name', '<unnamed>')}: one_post_outlier requires role_scope=post_specimen"
            )

    total = sum(effective_values[key] / 5 * weight for key, weight in WEIGHTS.items())
    gates = candidate.get("gates", {})
    capped = False
    cap_reason = None
    if role_scope == "core" and gates.get("audience_problem_match") == "fail" and total > 59:
        total, capped, cap_reason = 59, True, "audience/problem mismatch"
    if gates.get("operational_replicability") == "fail" and total > 64:
        total, capped, cap_reason = 64, True, "operational mismatch"

    if role_scope == "post_specimen":
        band = "post-level specimen"
    elif role_scope == "specialist" and total >= 65:
        band = "useful specialist benchmark"
    elif role_scope == "specialist" and total >= 50:
        band = "narrow specialist inspiration"
    elif role_scope == "specialist":
        band = "reject"
    elif total >= 80:
        band = "strong core benchmark"
    elif total >= 65:
        band = "useful role benchmark"
    elif total >= 50:
        band = "inspiration only"
    else:
        band = "reject"

    result = dict(candidate)
    tier = candidate.get("tier")
    tier_values = candidate.get("tier_scores")
    tier_learning_score = None
    if tier_values is not None:
        if tier not in TIER_WEIGHTS:
            raise ValueError(f"{candidate.get('name', '<unnamed>')}: tier must be large, medium, or small")
        missing_tier = [key for key in TIER_WEIGHTS[tier] if key not in tier_values]
        if missing_tier:
            raise ValueError(f"{candidate.get('name', '<unnamed>')}: missing tier scores {missing_tier}")
        for key, value in tier_values.items():
            if key in TIER_WEIGHTS[tier] and (not isinstance(value, (int, float)) or not 0 <= value <= 5):
                raise ValueError(f"{candidate.get('name', '<unnamed>')}: {key} must be 0..5")
        tier_learning_score = round(
            sum(tier_values[key] / 5 * weight for key, weight in TIER_WEIGHTS[tier].items()), 1
        )
    temperament_values = candidate.get("temperament_scores")
    temperament_fit_score = None
    if temperament_values is not None:
        missing_temperament = [key for key in TEMPERAMENT_WEIGHTS if key not in temperament_values]
        if missing_temperament:
            raise ValueError(
                f"{candidate.get('name', '<unnamed>')}: missing temperament scores {missing_temperament}"
            )
        for key, value in temperament_values.items():
            if key in TEMPERAMENT_WEIGHTS and (
                not isinstance(value, (int, float)) or not 0 <= value <= 5
            ):
                raise ValueError(f"{candidate.get('name', '<unnamed>')}: {key} must be 0..5")
        temperament_fit_score = round(
            sum(
                temperament_values[key] / 5 * weight
                for key, weight in TEMPERAMENT_WEIGHTS.items()
            ),
            1,
        )
    result.update(
        weighted_score=round(total, 1),
        role_scope=role_scope,
        tier_learning_score=tier_learning_score,
        temperament_fit_score=temperament_fit_score,
        band=band,
        provisional=gates.get("current_evidence") == "unknown",
        capped=capped,
        cap_reason=cap_reason,
        score_adjustments=score_adjustments,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON file containing a list of candidates")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    candidates = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(candidates, list):
        raise ValueError("input must be a JSON list")
    ranked = sorted(
        (score(item) for item in candidates),
        key=lambda item: (item.get("tier") or "", item.get("tier_learning_score") or item["weighted_score"]),
        reverse=True,
    )
    print(json.dumps(ranked, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
