# Scoring and decision rules

## Contents

1. Sequence
2. Six core gates
3. Three distribution gates
4. Ten score dimensions
5. Numeric bands
6. Final decisions
7. Validation tasks and metrics
8. Duplicate test

## 1. Sequence

Apply the three distribution gates and six core gates, record evidence, score for comparison, then make an analyst judgment. Never sort by score before gates are reviewed.

## 2. Six core gates

Use `pass`, `repairable_fail`, or `fail`.

| Gate | Pass question | Typical failure |
|---|---|---|
| Qualification | Does the creator have direct experience, a method, a result, or legitimate authority for this claim? | Hot topic outside creator competence |
| Audience fit | Is the likely responding audience substantially the intended audience? | Tool collectors, bargain seekers, students, or broad anxiety traffic dominate |
| Reality/proof | Is there a real event and public-safe proof, or a dated route to obtain it? | Empty opinion, invented scene, unsupported result |
| Strategic fit | Does it serve positioning, a content pillar, and a plausible long-term direction? | Unrelated trend or vanity traffic |
| Distinctness | Does it test a different problem, mechanism, event, or hypothesis? | Same viewpoint with another title or number |
| Integrity | Can it work without fear, exaggeration, false urgency, fabricated conflict, or privacy exploitation? | Anxiety bait, fake authority, exposed child/client/family data |

Interpretation:

- `fail`: current core is invalid; normally `eliminate`.
- `repairable_fail`: current version cannot publish, but a named evidence item or angle change can repair it; use `rewrite` or `observe`.
- `pass`: no blocking issue detected; still record risks.

Before scoring, also record the three-axis judgment:

| Axis | Pass evidence | Failure pattern |
|---|---|---|
| Difference | A distinct event, mechanism, proof, contradiction, or hypothesis | New title or synonym only; copied sequence |
| Relevance | Named user stage/trigger plus positioning and task fit | Broad heat or wrong audience |
| Usefulness | A decision, action, recognition, comparison, or reusable object | Generic viewpoint or empty emotional uplift |

These axes explain the existing gates and score dimensions; they do not add bonus points. Record one primary value mode and one evidence-earned cognitive increment.

## 3. Three distribution gates

Use `pass`, `repairable_fail`, or `fail`. Record the evidence behind each result.

| Gate | Pass question | Pass evidence | Typical failure |
|---|---|---|---|
| Counterintuitive | Does the topic overturn a credible prior belief and replace it with a useful judgment? | `prior belief -> evidence-backed contradiction -> replacement judgment` | Familiar advice, empty provocation, surprising title only |
| Shared scene | Do many intended users repeatedly face the same job, trigger, conflict, or decision? | Repeated target-user behavior/language across independent source clusters, with sample and limitation; the common job remains true even when the creator artifact is niche | One creator case, one viral post, broad emotion, or wrong-audience heat |
| Forwarding job | Can the target user name who should receive it and what the share says for them? | Recipient, share sentence, and social function such as alignment, warning, recognition, or permission | “Useful so people may share”; no recipient or communicative job |

Do not require the audience to use the creator's exact artifact. A website audit can prove an AI-review mechanism, but it does not prove that website auditing is common. The shared scene must be expressed at the smallest truthful common-job level, such as a founder repeatedly reviewing AI-generated customer, content, hiring, or strategy outputs.

Evidence rules for `shared_scene`:

- `pass`: the same target-user job or trigger recurs across at least two independent evidence clusters, such as platform comments/search records plus interviews, first-party task records, payment behavior, or another auditable source. Record observed sample size and limitations; do not claim platform prevalence.
- `repairable_fail`: the scene is plausible and appears more than once, but evidence comes from one narrow source or the current angle foregrounds a niche artifact.
- `fail`: only the creator case, a borrowed hit, or an inference supports the scene.

Distribution policies:

- `strict_shareability`: `keep` requires all three distribution gates to pass for every topic.
- `task_calibrated`: attention topics require all three to pass. Trust/commercial topics may remain `keep` with a documented `narrow_role_basis`; do not claim broad propagation.

The gates prevent a score from laundering weak propagation. `novel_angle` and `user_demand` still help compare topics that pass; they do not replace the gates.

## 4. Ten score dimensions

Score only with cited evidence.

Attribute creator/teacher claims separately. Self-reported algorithm weights, viral standards, revenue, or performance thresholds cannot raise `user_demand`, `creator_proof`, or `metric_match` unless current primary or account-level evidence supports the exact claim.

| Code | Dimension | Max | High-score evidence |
|---|---|---:|---|
| `user_demand` | Users really have/ask the problem | 15 | Direct quotes, repeated behavior, search/comment patterns, payment or cost evidence |
| `search_save` | Clear search, decision, reuse, or collection need | 10 | Natural query language, checklist/template/case reuse, recurring task |
| `creator_proof` | Creator qualification and usable proof | 15 | First-party event, before/after, artifact, method, result, permission |
| `strategic_fit` | Positioning, pillar, audience, and offer fit | 15 | Directly advances current content and commercial thesis |
| `novel_angle` | New interpretation without copying | 10 | Distinct mechanism, contradiction, first-party case, or decision rule |
| `series_potential` | Can become a genuine recurring column | 8 | At least three future episodes with different events/evidence/hypotheses |
| `audience_precision` | Attracts intended users and filters wrong ones | 10 | Language implies the right stage, cost, role, and constraints |
| `integrity` | Works without manipulation or unsupported claims | 7 | Factual, bounded, privacy-safe, non-alarmist framing |
| `validation_clarity` | Tests one attention/trust/commercial hypothesis | 5 | One falsifiable claim and one task |
| `metric_match` | Post metrics diagnose that hypothesis | 5 | One baseline-relative primary metric plus declared windows |

Score anchors:

- 0: absent or contradicted;
- about 40% of max: plausible but C/D evidence;
- about 70% of max: useful B evidence with a named gap;
- full or near-full: direct A evidence and little ambiguity.

## 5. Numeric bands

- `strong`: 80-100;
- `conditional`: 65-79;
- `weak`: 0-64.

These bands never override a gate. A high-score topic can remain `observe` when proof is not yet available. A modest-search topic can be `keep` when it is a strong first-party trust or commercial test.

## 6. Final decisions

### Keep

Require all applicable distribution and core gates to pass, proof available before production, score normally at least 80, and a clear experiment. Under `task_calibrated`, a narrow trust/commercial exception requires an explicit `narrow_role_basis`.

### Rewrite

Use when the user problem is useful but the current angle, search framing, audience filter, evidence framing, or differentiation is repairable now. Name the replacement angle and required proof.

### Observe

Use when a strategically important topic is blocked by missing demand evidence, a future experiment result, permission, or a first-party case. Name a dated or observable unlock condition. Do not schedule before it is met.

### Eliminate

Use when the creator lacks legitimate qualification, the topic primarily attracts the wrong audience, there is no real event/proof path, it is unrelated to positioning/products, it duplicates another hypothesis, or it needs fear/exaggeration/fiction.

## 7. Validation tasks and metrics

| Task | Primary evidence options | Diagnostic supporting metrics |
|---|---|---|
| Attention | Target-profile visit rate, target-follow rate, target-problem comment rate, search-entry share, or share rate when propagation is the declared single hypothesis | Completion, saves, share recipients inferred from qualified comments |
| Trust | Qualified save rate, specific-method question rate, qualified DM rate | Completion, rewatch, profile visits |
| Commercial | Qualified-task description rate, qualified inquiry rate, booked/paid next step when in scope | Saves, profile visits, comments |

Define `target` and `qualified` before publication. Use the creator's comparable-format baseline. Review early signals around 24 hours and make a topic decision around 7 days unless another cadence is declared.

## 8. Duplicate test

Treat two candidates as the same topic when all four are substantially identical:

1. user job;
2. trigger moment;
3. core mechanism or claim;
4. proof and single hypothesis.

A new title, list length, emotion word, or platform packaging is not a new topic. Keep the version with stronger proof and audience precision; log the merge.
