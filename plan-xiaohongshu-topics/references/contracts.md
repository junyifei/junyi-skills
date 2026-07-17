# Input and output contracts

## Contents

1. Scope boundary
2. Upstream user-insight input
3. Creator-context input
4. Topic batch output
5. Downstream topic brief
6. Missing-data behavior

## 1. Scope boundary

The upstream user-insight skill owns collection, market sampling, interview analysis, pain synthesis, and evidence grading. This skill preserves those records and turns them into topic tests. The downstream content skill owns structure, full copy, shot list, captions, and platform-ready draft. The review skill owns fact checking, style, compliance, and revision.

## 2. Upstream user-insight input

Use one record per distinct user problem or job:

| Field | Type | Rule |
|---|---|---|
| `insight_id` | string | Stable unique identifier |
| `user_quote` | string or null | Exact wording only; null when unavailable |
| `real_scene` | string | Observable time, place, event, and constraint |
| `user_problem` | string | Problem in user terms, not creator solution language |
| `emotion_and_cost` | object | Emotional state plus time, money, risk, relationship, or opportunity cost |
| `job_to_be_done` | string | What the user is trying to complete |
| `expected_change` | string | Observable desired before/after change |
| `signal_source` | object | Source type, locator, date, sample notes, and limitations |
| `evidence_grade` | enum | `A`, `B`, `C`, or `D` |
| `time_range` | object | Start/end or snapshot date |
| `creator_relevance` | object | Score/reason for fit with positioning, pillars, and offer |

Evidence grades:

- `A`: repeated first-party user evidence or direct behavioral/payment evidence with source detail;
- `B`: one direct source plus corroborating signals, or repeated credible public signals;
- `C`: plausible but mostly inferred, small-sample, or unverified;
- `D`: unsupported, stale, contradictory, or impossible to audit.

Do not translate a creator belief into `user_quote`.

## 3. Creator-context input

```json
{
  "creator": {
    "positioning": "",
    "target_audiences": [],
    "excluded_audiences": [],
    "content_pillars": [{"name": "", "role": "", "target_share": null}],
    "offers": [{"name": "", "target_buyer": "", "evidence_status": ""}],
    "proof_inventory": [{"proof_id": "", "type": "", "claim_supported": "", "available_now": false, "public_permission": ""}],
    "ethical_boundaries": [],
    "distribution_policy": "strict_shareability|task_calibrated",
    "account_baselines": [{"format": "", "window": "", "metrics": {}}]
  }
}
```

## 4. Topic batch output

```json
{
  "batch_id": "",
  "platform": "xiaohongshu",
  "created_at": "YYYY-MM-DD",
  "source_snapshot": [],
  "deduplication_log": [],
  "topics": [],
  "batch_summary": {
    "keep": 0,
    "rewrite": 0,
    "observe": 0,
    "eliminate": 0,
    "coverage_by_pillar": {},
    "coverage_by_validation_task": {}
  }
}
```

## 5. Downstream topic brief

Every final topic must contain at least these fields:

```json
{
  "topic_id": "",
  "upstream_insights": [{
    "insight_id": "",
    "user_quote": null,
    "source": {},
    "evidence_grade": "B",
    "use_in_topic": ""
  }],
  "target_user": {
    "identity": "",
    "stage": "",
    "included": [],
    "excluded": []
  },
  "trigger_moment": "",
  "search_intent": {
    "intent_type": "problem|solution|comparison|decision|case|none",
    "query_language": [],
    "save_reason": ""
  },
  "topic_angle": "",
  "three_axis_check": {
    "difference": "",
    "relevance": "",
    "usefulness": ""
  },
  "value_mode": {
    "primary": "method|aesthetic|emotional_understanding",
    "secondary": null,
    "user_receives": ""
  },
  "cognitive_increment": {
    "before_belief_or_action": "",
    "after_belief_or_action": "",
    "earned_by_proof_ids": []
  },
  "title_direction": [],
  "hook_direction": "",
  "distribution_policy": "strict_shareability|task_calibrated",
  "distribution_gates": {
    "counterintuitive": {
      "prior_belief": "",
      "contradicting_evidence": [],
      "replacement_judgment": "",
      "result": "pass|repairable_fail|fail"
    },
    "shared_scene": {
      "common_job_or_trigger": "",
      "evidence_clusters": [],
      "sample_and_limitations": "",
      "result": "pass|repairable_fail|fail"
    },
    "forwarding_job": {
      "recipient": "",
      "share_sentence": "",
      "social_function": "alignment|warning|recognition|permission|other",
      "result": "pass|repairable_fail|fail"
    }
  },
  "primary_content_task": "attention|trust|commercial",
  "creator_real_material": [],
  "attributed_source_claims": [],
  "required_proof": [],
  "recommended_format": "",
  "expected_metrics": {
    "primary": "",
    "supporting": [],
    "baseline": "",
    "early_window": "24h",
    "decision_window": "7d"
  },
  "current_evidence_grade": "A|B|C|D",
  "single_hypothesis": "",
  "risks": {
    "wrong_audiences": [],
    "triggering_language": [],
    "integrity_privacy": [],
    "mitigations": []
  },
  "score": {
    "dimensions": {},
    "total": 0,
    "numeric_band": "strong|conditional|weak"
  },
  "gate_results": {},
  "decision": "keep|rewrite|observe|eliminate",
  "decision_basis": "",
  "unlock_condition": null,
  "downstream_constraints": {
    "must_preserve": [],
    "must_not_claim": [],
    "do_not_write_full_post_here": true
  }
}
```

`expected_metrics.primary` must be one metric or one composite explicitly defined in the baseline. Views and likes alone are not adequate primary evidence.

## 6. Missing-data behavior

- Missing user quote: preserve null; use a documented source summary, never fabricated wording.
- Missing creator proof: `observe` if a dated proof item can arrive; otherwise `eliminate` or `rewrite`.
- Missing demand evidence: do not score user demand above the C-evidence range; run a bounded test only when strategic fit and integrity pass.
- Missing counterintuitive evidence: familiar advice does not pass because the title sounds surprising; use `rewrite` or `eliminate`.
- Missing shared-scene evidence: preserve the creator case as proof, but use `observe` until repeated target-user behavior is documented. Under `strict_shareability`, do not schedule it.
- Missing forwarding job: use `rewrite` until a specific recipient and communicative function can be named; “people may find it useful” is not enough.
- Missing baseline: state `baseline unavailable` and use the first comparable posts to establish it before claiming success.
- Missing permission: prohibit the asset from public use; anonymization is not a substitute when the case remains identifiable.
- Creator/teacher claim only: retain speaker, date, locator, scope, and caveat; use it as a hypothesis or illustrative experience, not platform truth or proof that the topic will perform.
