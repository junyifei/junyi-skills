---
name: plan-xiaohongshu-topics
description: Discover, generate, deduplicate, screen, score, and rank Xiaohongshu topic hypotheses from validated user insights and creator evidence, including counterintuitive insight, shared-scene, and forwarding-job checks for shareability. Use when planning 小红书选题、内容栏目、选题池、选题评级、传播潜力、发布测试、标题方向或从用户问题生成可测试内容简报. Do not use for deep pain-point research, full post writing, final copy review, or publishing.
---

# Plan Xiaohongshu Topics

Turn upstream user evidence into a small set of Xiaohongshu topic hypotheses that a creator is qualified to publish and able to test. Treat scores as comparison aids, never as substitutes for evidence and judgment.

## Keep the boundary

Place this skill between user-insight research and content creation:

`user evidence -> this skill -> tested topic brief -> content creation -> review/edit`

Do not perform a full market study, write the full post, review a finished draft, or publish. If upstream evidence is missing, label the gap and choose `observe`; do not invent user quotes or demand.

Read [contracts.md](references/contracts.md) before accepting upstream data or handing work downstream. Read [scoring.md](references/scoring.md) before rating any candidate. Read [generalization-tests.md](references/generalization-tests.md) when changing contracts, gates, or scoring logic.

## Run the workflow

### 1. Load creator constraints

Collect only what topic judgment needs:

- positioning and audience;
- current content pillars and intended proportion;
- products or commercial direction;
- first-party experiences, methods, results, failures, artifacts, and permissions;
- source-claim status for creator/teacher statements about algorithms, viral standards, revenue, or performance thresholds;
- excluded audiences and ethical boundaries;
- distribution policy: `strict_shareability` when every scheduled topic must earn sharing, or `task_calibrated` when narrow trust/commercial topics may be kept deliberately;
- recent account baseline by comparable format.

If creator evidence is only promised, distinguish `available now` from `obtainable before publication`.

### 2. Validate upstream insight records

Require the 11 upstream fields in [contracts.md](references/contracts.md). Preserve exact user wording and source metadata. Do not upgrade an inference into a quote.

Accept partial records only when the missing fields do not change the decision. Otherwise return a compact `missing_evidence` list and keep the candidate in `observe` or `eliminate`.

### 3. Collapse pseudo-topics

Group records by the same user job, trigger moment, mechanism, and promised change. Treat title variations as one topic when they test the same claim with the same proof.

Keep one canonical topic and record the discarded variants as duplicates. Do not count a new number, adjective, or emotional phrase as a new angle.

### 4. Generate distinct candidate angles

Generate two to four angles per validated insight only when they test materially different hypotheses. Prefer:

- problem naming;
- real-event or failure postmortem;
- mechanism or decision rule;
- before/after comparison;
- checklist or template with a real use case;
- bounded experiment or data review.

Borrow demand language, not popular titles. Anchor each angle in one trigger moment and one creator asset.

For a public hit, keep only the underlying audience demand or abstract structure. Do not copy its title, distinctive wording, personal story, data, screenshots, sequence, or proof. Use `same demand, different evidence`.

### 5. Test difference, relevance, and usefulness

Before the hard gates, answer three questions with evidence:

- `差异性`: what new event, mechanism, proof, contradiction, or testable judgment exists beyond a new title?
- `相关性`: which target user's stage and trigger does it serve, and how does it fit the creator's positioning and current task?
- `实用性`: what can the user decide, do, notice, compare, or save after consuming it?

Choose one primary value mode: `方法价值 / 审美价值 / 情绪理解`. Name the concrete cognitive increment: `看前的认知/动作 -> 内容凭什么改变它 -> 看后的认知/动作`. A topic may be emotionally valuable without a checklist, but `情绪理解` must still offer precise recognition rather than generic comfort.

### 6. Apply the distribution gates

Read the distribution-gate rules in [scoring.md](references/scoring.md). Test three separate conditions:

- `counterintuitive`: name the target user's credible prior belief, the creator evidence that contradicts it, and the replacement judgment. Correct but familiar advice does not pass. Manufactured opposition, fear, or a surprising title without evidence fails.
- `shared_scene`: prove that the target audience repeatedly encounters the same job, trigger, conflict, or decision. The creator's exact artifact may be niche; translate it to the common job without hiding the proof. One creator story or one viral post cannot establish breadth.
- `forwarding_job`: name who the target user would send it to, what the share helps them say, and why sharing is easier than explaining it themselves.

Use the creator's declared distribution policy:

- Under `strict_shareability`, every scheduled topic must pass all three gates. A true but niche story remains evidence, not a publishable topic, until it is re-angled to a proven shared scene.
- Under `task_calibrated`, attention topics must pass all three. A narrow trust or commercial topic may proceed only with a named narrow role and must not be described as broadly shareable.

Do not confuse broad heat with a shared scene. Require repeated target-audience behavior or language with source detail; tool traffic or a broad emotional audience does not satisfy the intended audience.

### 7. Apply the six core gates before scoring

Test all six gates in [scoring.md](references/scoring.md): qualification, audience fit, reality/proof, strategic fit, distinctness, and integrity.

A failed current version cannot be published. A creator/teacher source claim cannot satisfy reality/proof or demand by itself. Mark it:

- `rewrite` only when a specific new angle plus obtainable evidence can repair it;
- `observe` when a dated event, proof item, or demand signal must arrive first;
- `eliminate` when it depends on the wrong audience, borrowed authority, empty opinion, unrelated trends, duplication, fear, exaggeration, or fiction.

### 8. Score surviving candidates

Score the ten dimensions out of 100 using [scoring.md](references/scoring.md). Cite evidence beside every non-zero score. Do not infer demand from trend heat alone.

Use `scripts/score_topics.py` to total and validate a batch:

```bash
python scripts/score_topics.py input.json --output scored.json
```

The script computes a numeric band and checks decision consistency. The analyst must still provide the final decision and rationale.

### 9. Define one experiment

Assign exactly one primary content task:

- `attention`: target users recognize themselves and visit/follow;
- `trust`: users understand the creator's method and ask specific questions;
- `commercial`: qualified users describe a real task or take a next step.

Write one falsifiable hypothesis and one primary metric. Use supporting metrics only for diagnosis. Compare with the creator's own comparable-format baseline; do not declare a universal viral threshold.

Observe an early window around 24 hours and a decision window around 7 days unless the account's cadence requires another declared window.

### 10. Hand off without writing the post

Return the complete `topic_brief` contract from [contracts.md](references/contracts.md). Include title and hook directions, not finished prose. Require the downstream content skill to preserve the target user, trigger moment, value mode, cognitive increment, creator proof, prohibited claims, single hypothesis, and primary metric.

## Make the final judgment

Use four decisions:

- `keep`: ready to schedule; all gates pass and proof is available;
- `rewrite`: core problem is useful, but angle, audience, search intent, proof framing, or differentiation must change;
- `observe`: strategically relevant but blocked by missing evidence, timing, or demand validation;
- `eliminate`: current topic should not enter the test pool.

Never rescue a candidate merely because its score is high. Never eliminate a strong first-party experiment merely because broad search heat is modest when its primary task is trust or commercial validation.

Under `strict_shareability`, do not use that exception: a topic blocked by counterintuitive, shared-scene, or forwarding-job evidence cannot be scheduled. Preserve the creator's true material in the evidence library and return the topic as `rewrite`, `observe`, or `eliminate`.

## Enforce output quality

- Keep user quote, creator fact, external signal, inference, and hypothesis visibly separate.
- Keep creator/teacher experience claims visibly attributed; do not convert a self-reported algorithm, income, viral threshold, or performance standard into a platform fact.
- Name the likely wrong audience and the language that would attract it.
- State the proof that must appear; `tell a story` is not proof.
- State the shared job rather than assuming the creator's exact incident is common.
- State the forwarding recipient and the sentence the share helps the user communicate.
- Reject familiar advice disguised by a surprising title; the contradiction must be earned by evidence.
- Reject unsupported income, capability, urgency, or family claims.
- Protect children, clients, students, partners, and private relationships.
- Keep a series only when future episodes can use different events, evidence, and hypotheses.
- Record why a duplicate was merged or removed.
- Do not publish or produce a full draft.
