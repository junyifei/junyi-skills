# Input and output specification

## Contents

1. Canonical input
2. Required deliverables
3. Canonical JSON contract
4. Markdown contract
5. Downstream topic-skill interface
6. Versioning

## 1. Canonical input

Accept natural language or this YAML-shaped contract:

```yaml
research_request:
  target_audience:
    description: ""
    reach_audience: ""
    likely_buyer: ""
    exclusions: []
  platforms: []
  seed_keywords: []
  benchmark_accounts: []
  time_range:
    start: "YYYY-MM-DD or unknown"
    end: "YYYY-MM-DD or unknown"
    comparison_period: "optional"
  business_question: ""
  creator_context:
    positioning: ""
    lived_assets: []
    proof: []
    constraints: []
    unknowns: []
  supplied_sources: []
  output_directory: ""
```

Resolve relative dates before research. Preserve missing fields as explicit assumptions or unknowns.

## 2. Required deliverables

Produce a pair with the same slug:

- `<slug>-audience-insights.md`: human-readable evidence report;
- `<slug>-audience-insights.json`: machine-readable canonical payload.

The JSON must pass `scripts/validate_output.py`. The Markdown must be traceable to the same source and claim IDs.

## 3. Canonical JSON contract

Use `schema_version: "1.0"`. Required top-level fields:

| Field | Purpose |
|---|---|
| `schema_version` | Interface version. |
| `research_id` | Stable run identifier. |
| `generated_at` | ISO 8601 time. |
| `research_request` | Normalized input. |
| `access_boundaries` | Per-platform access and limits. |
| `sample_summary` | Queries, content, comments, users, accounts, and selection rules. |
| `sources` | Source ledger. |
| `verbatims` | Exact short audience language with provenance. |
| `questions` | Explicit and normalized user questions. |
| `scenes` | Triggered real-world contexts and consequences. |
| `problem_clusters` | Surface problems, costs, jobs, frequency, value, horizon, creator fit. |
| `before_after_map` | Observable audience transitions. |
| `creator_fit` | Creator evidence and gaps by problem. |
| `claims` | Facts, inferences, hypotheses, and unknowns. |
| `unknowns` | Decision-relevant next research gaps. |
| `downstream_handoff` | What a topic skill may use and must not overclaim. |

Required enums:

```text
claim_status: fact | inference | hypothesis | unknown
evidence_grade: A | B | C | D | U
access_mode: in_platform_live | public_web | user_supplied | unavailable
relevance: high | medium | low
response_readiness: proven | plausible | weak | unknown
horizon: short_term_hot | long_term_stable | mixed | insufficient_history
frequency_band: high-frequency | medium-frequency | low-frequency | insufficient-sample
value_band: high-value | medium-value | low-value | unknown-value
```

Every verbatim needs at least one valid `source_id`. Every consequential synthesis item needs `claim_status`, `evidence_grade`, and `source_ids`; an `unknown` may use an empty `source_ids` list if the absence itself is explained.

Every problem cluster must include:

- surface statement;
- linked question, scene, and verbatim IDs when available;
- emotions and typed costs;
- workaround;
- functional/emotional/social jobs;
- success state;
- frequency and value bands with rationale;
- horizon with rationale;
- creator relevance and response readiness;
- evidence labels and source IDs.

## 4. Markdown contract

Use the bundled report template and keep this section order:

1. Research decision boundary
2. Scope, access, and sample
3. Executive audience insight
4. User verbatim library
5. User question library
6. Real-scene library
7. Emotions, costs, and unfinished jobs
8. Before-after map
9. High-frequency versus high-value problems
10. Short-term heat versus long-term need
11. Creator-position relevance and proof
12. Claims ledger
13. Unknowns and next research
14. Downstream handoff

Use tables for libraries. Include IDs so downstream tools can join data across files.

## 5. Downstream topic-skill interface

A downstream topic skill should read the JSON first and may use only:

- `problem_clusters` whose `claim_status` is `fact` or `inference`;
- linked `verbatim_ids`, `question_ids`, and `scene_ids`;
- `before_after_map`;
- `creator_fit` with `response_readiness` of `proven` or `plausible`;
- `downstream_handoff.allowed_claim_ids` and `recommended_problem_ids`.

It must preserve source/claim IDs in its internal reasoning and must not:

- turn a hypothesis into a user fact;
- quote a normalized question as verbatim;
- call a public-web trend an in-platform live trend;
- call an attention signal paid demand;
- use a `weak` or `unknown` creator response readiness as authority without a validation frame;
- use `unknowns` as positive evidence.
- turn a creator/teacher's algorithm, viral-standard, income, or threshold claim into platform fact, user demand, or a benchmark without independent primary evidence.

Recommended topic-input envelope:

```json
{
  "interface": "audience-insights-to-topic-skill",
  "interface_version": "1.0",
  "source_research_id": "...",
  "recommended_problem_ids": [],
  "allowed_claim_ids": [],
  "verbatim_ids": [],
  "question_ids": [],
  "scene_ids": [],
  "before_after_ids": [],
  "creator_fit_ids": [],
  "prohibited_overclaims": []
}
```

## 6. Versioning

Backward-compatible additions may keep version `1.x`. Rename or remove canonical fields only in a new major version. Downstream skills must reject unsupported major versions rather than guessing.
