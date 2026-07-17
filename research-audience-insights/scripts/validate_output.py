#!/usr/bin/env python3
"""Validate the canonical audience-insights JSON without third-party packages."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_TOP = {
    "schema_version",
    "research_id",
    "generated_at",
    "research_request",
    "access_boundaries",
    "sample_summary",
    "sources",
    "verbatims",
    "questions",
    "scenes",
    "problem_clusters",
    "before_after_map",
    "creator_fit",
    "claims",
    "unknowns",
    "downstream_handoff",
}
CLAIM_STATUSES = {"fact", "inference", "hypothesis", "unknown"}
GRADES = {"A", "B", "C", "D", "U"}
ACCESS_MODES = {"in_platform_live", "public_web", "user_supplied", "unavailable"}
RELEVANCE = {"high", "medium", "low"}
READINESS = {"proven", "plausible", "weak", "unknown"}
HORIZONS = {"short_term_hot", "long_term_stable", "mixed", "insufficient_history"}
FREQUENCIES = {"high-frequency", "medium-frequency", "low-frequency", "insufficient-sample"}
VALUES = {"high-value", "medium-value", "low-value", "unknown-value"}


def as_list(data: dict, key: str, errors: list[str]) -> list:
    value = data.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    return value


def require(item: dict, keys: set[str], where: str, errors: list[str]) -> None:
    missing = sorted(k for k in keys if k not in item)
    if missing:
        errors.append(f"{where} missing: {', '.join(missing)}")


def unique_ids(items: list, id_key: str, where: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{where}[{index}] must be an object")
            continue
        value = item.get(id_key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{where}[{index}].{id_key} must be a non-empty string")
        elif value in seen:
            errors.append(f"duplicate {id_key}: {value}")
        else:
            seen.add(value)
    return seen


def check_evidence(item: dict, where: str, errors: list[str], allow_empty_sources: bool = False) -> None:
    status = item.get("claim_status")
    grade = item.get("evidence_grade")
    source_ids = item.get("source_ids")
    if status not in CLAIM_STATUSES:
        errors.append(f"{where}.claim_status invalid: {status!r}")
    if grade not in GRADES:
        errors.append(f"{where}.evidence_grade invalid: {grade!r}")
    if not isinstance(source_ids, list):
        errors.append(f"{where}.source_ids must be a list")
    elif not source_ids and not (allow_empty_sources and status == "unknown"):
        errors.append(f"{where}.source_ids must not be empty")


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    missing_top = sorted(REQUIRED_TOP - data.keys())
    if missing_top:
        errors.append("missing top-level fields: " + ", ".join(missing_top))
    if data.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if not str(data.get("research_id", "")).strip():
        errors.append("research_id must be non-empty")

    request = data.get("research_request")
    if not isinstance(request, dict):
        errors.append("research_request must be an object")
    else:
        require(
            request,
            {"target_audience", "platforms", "seed_keywords", "benchmark_accounts", "time_range", "business_question", "creator_context", "supplied_sources"},
            "research_request",
            errors,
        )
        if not isinstance(request.get("platforms"), list) or not request.get("platforms"):
            errors.append("research_request.platforms must be a non-empty list")
        if not str(request.get("business_question", "")).strip():
            errors.append("research_request.business_question must be non-empty")

    boundaries = as_list(data, "access_boundaries", errors)
    for i, item in enumerate(boundaries):
        if not isinstance(item, dict):
            continue
        require(item, {"platform", "access_mode", "captured_at", "limitations"}, f"access_boundaries[{i}]", errors)
        if item.get("access_mode") not in ACCESS_MODES:
            errors.append(f"access_boundaries[{i}].access_mode invalid")

    sources = as_list(data, "sources", errors)
    source_ids = unique_ids(sources, "source_id", "sources", errors)
    for i, item in enumerate(sources):
        if not isinstance(item, dict):
            continue
        require(item, {"source_id", "platform", "source_type", "access_mode", "captured_at", "url_or_artifact", "provenance_note"}, f"sources[{i}]", errors)
        if item.get("access_mode") not in ACCESS_MODES:
            errors.append(f"sources[{i}].access_mode invalid")

    collections = {
        "verbatims": "verbatim_id",
        "questions": "question_id",
        "scenes": "scene_id",
        "problem_clusters": "problem_id",
        "before_after_map": "map_id",
        "creator_fit": "fit_id",
        "claims": "claim_id",
        "unknowns": "unknown_id",
    }
    id_sets: dict[str, set[str]] = {}
    for key, id_key in collections.items():
        id_sets[key] = unique_ids(as_list(data, key, errors), id_key, key, errors)

    for i, item in enumerate(data.get("verbatims", [])):
        if not isinstance(item, dict):
            continue
        require(item, {"verbatim_id", "text", "context", "speaker_scope", "claim_status", "evidence_grade", "source_ids"}, f"verbatims[{i}]", errors)
        check_evidence(item, f"verbatims[{i}]", errors)

    for key in ("questions", "scenes", "before_after_map", "claims"):
        for i, item in enumerate(data.get(key, [])):
            if isinstance(item, dict):
                check_evidence(item, f"{key}[{i}]", errors, allow_empty_sources=(key == "claims"))

    for i, item in enumerate(data.get("problem_clusters", [])):
        if not isinstance(item, dict):
            continue
        require(
            item,
            {
                "problem_id", "surface_problem", "verbatim_ids", "question_ids", "scene_ids",
                "emotions", "costs", "current_workaround", "functional_job", "emotional_job",
                "social_job", "success_state", "frequency_band", "frequency_rationale", "value_band",
                "value_rationale", "horizon", "horizon_rationale", "creator_relevance",
                "response_readiness", "claim_status", "evidence_grade", "source_ids",
            },
            f"problem_clusters[{i}]",
            errors,
        )
        check_evidence(item, f"problem_clusters[{i}]", errors)
        if item.get("frequency_band") not in FREQUENCIES:
            errors.append(f"problem_clusters[{i}].frequency_band invalid")
        if item.get("value_band") not in VALUES:
            errors.append(f"problem_clusters[{i}].value_band invalid")
        if item.get("horizon") not in HORIZONS:
            errors.append(f"problem_clusters[{i}].horizon invalid")
        if item.get("creator_relevance") not in RELEVANCE:
            errors.append(f"problem_clusters[{i}].creator_relevance invalid")
        if item.get("response_readiness") not in READINESS:
            errors.append(f"problem_clusters[{i}].response_readiness invalid")
        for field, valid_ids in (
            ("verbatim_ids", id_sets["verbatims"]),
            ("question_ids", id_sets["questions"]),
            ("scene_ids", id_sets["scenes"]),
        ):
            for value in item.get(field, []):
                if value not in valid_ids:
                    errors.append(f"problem_clusters[{i}].{field} references unknown id {value!r}")

    for i, item in enumerate(data.get("questions", [])):
        if not isinstance(item, dict):
            continue
        scene_id = item.get("scene_id")
        if scene_id and scene_id not in id_sets["scenes"]:
            errors.append(f"questions[{i}].scene_id references unknown id {scene_id!r}")

    for i, item in enumerate(data.get("before_after_map", [])):
        if not isinstance(item, dict):
            continue
        if item.get("problem_id") not in id_sets["problem_clusters"]:
            errors.append(f"before_after_map[{i}].problem_id does not exist")

    for i, item in enumerate(data.get("creator_fit", [])):
        if not isinstance(item, dict):
            continue
        require(item, {"fit_id", "problem_id", "relevance", "response_readiness", "owned_evidence", "missing_proof", "boundary", "claim_status", "evidence_grade", "source_ids"}, f"creator_fit[{i}]", errors)
        check_evidence(item, f"creator_fit[{i}]", errors)
        if item.get("relevance") not in RELEVANCE:
            errors.append(f"creator_fit[{i}].relevance invalid")
        if item.get("response_readiness") not in READINESS:
            errors.append(f"creator_fit[{i}].response_readiness invalid")
        if item.get("problem_id") not in id_sets["problem_clusters"]:
            errors.append(f"creator_fit[{i}].problem_id does not exist")

    all_source_refs: list[tuple[str, str]] = []
    for key in ("verbatims", "questions", "scenes", "problem_clusters", "before_after_map", "creator_fit", "claims"):
        for i, item in enumerate(data.get(key, [])):
            if isinstance(item, dict):
                for source_id in item.get("source_ids", []):
                    all_source_refs.append((f"{key}[{i}]", source_id))
    for where, source_id in all_source_refs:
        if source_id not in source_ids:
            errors.append(f"{where} references unknown source_id {source_id!r}")

    handoff = data.get("downstream_handoff")
    if not isinstance(handoff, dict):
        errors.append("downstream_handoff must be an object")
    else:
        require(handoff, {"interface", "interface_version", "source_research_id", "recommended_problem_ids", "allowed_claim_ids", "verbatim_ids", "question_ids", "scene_ids", "before_after_ids", "creator_fit_ids", "prohibited_overclaims"}, "downstream_handoff", errors)
        if handoff.get("interface") != "audience-insights-to-topic-skill":
            errors.append("downstream_handoff.interface invalid")
        if handoff.get("interface_version") != "1.0":
            errors.append("downstream_handoff.interface_version invalid")
        if handoff.get("source_research_id") != data.get("research_id"):
            errors.append("downstream_handoff.source_research_id must equal research_id")
        reference_map = {
            "recommended_problem_ids": id_sets["problem_clusters"],
            "allowed_claim_ids": id_sets["claims"],
            "verbatim_ids": id_sets["verbatims"],
            "question_ids": id_sets["questions"],
            "scene_ids": id_sets["scenes"],
            "before_after_ids": id_sets["before_after_map"],
            "creator_fit_ids": id_sets["creator_fit"],
        }
        for field, valid_ids in reference_map.items():
            for value in handoff.get(field, []):
                if value not in valid_ids:
                    errors.append(f"downstream_handoff.{field} references unknown id {value!r}")
        problem_status = {item.get("problem_id"): item.get("claim_status") for item in data.get("problem_clusters", []) if isinstance(item, dict)}
        claim_status = {item.get("claim_id"): item.get("claim_status") for item in data.get("claims", []) if isinstance(item, dict)}
        for value in handoff.get("recommended_problem_ids", []):
            if problem_status.get(value) not in {"fact", "inference"}:
                errors.append(f"downstream_handoff.recommended_problem_ids cannot include non-evidence claim {value!r}")
        for value in handoff.get("allowed_claim_ids", []):
            if claim_status.get(value) not in {"fact", "inference"}:
                errors.append(f"downstream_handoff.allowed_claim_ids cannot include {claim_status.get(value)!r} claim {value!r}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_output.py <audience-insights.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict):
        print("INVALID: top level must be an object", file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
