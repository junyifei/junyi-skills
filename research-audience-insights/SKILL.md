---
name: research-audience-insights
description: Research what an audience currently notices, experiences, asks, says verbatim, pays for, and is trying to accomplish. Use for 用户洞察、痛点调研、评论区研究、需求研究、用户原话、真实场景、JTBD、before-after 变化、平台热词与联想词、竞品评论、短期热点与长期需求区分、创作者问题匹配，或为后续选题/产品/定位提供标准化证据包。Do not use it to generate topics directly; produce evidence-grounded audience insights for downstream work.
---

# Research Audience Insights

Run one complete research cycle per invocation. Produce an evidence package, not a topic list.

## Required inputs

Collect or infer only when safe:

- target audience;
- research platforms;
- seed keywords;
- benchmark accounts or content;
- time range;
- business question;
- creator positioning, lived assets, proof, constraints, and unknowns.

If an input is absent, state the assumption. Do not invent account handles, access, proof, or user demand.

## Read before research

Read these files completely:

- [research-protocol.md](references/research-protocol.md) for sampling, evidence, analysis, and safety rules.
- [input-output-spec.md](references/input-output-spec.md) for canonical inputs and outputs.

Use [report-template.md](assets/report-template.md) and [audience-insights.template.json](assets/audience-insights.template.json) as output skeletons. Keep the canonical JSON field names unchanged.

## Workflow

### 1. Restate the research contract

Write the target audience as a situation plus constraints, not only a demographic label. Convert the business question into one to three research questions. Record the requested time range and the creator evidence to be tested.

### 2. Audit access before collecting

For every platform, record one access mode:

- `in_platform_live`: current, auditable in-platform search or comment access;
- `public_web`: public pages or search-engine-visible material only;
- `user_supplied`: supplied exports, screenshots, reports, transcripts, or links;
- `unavailable`: no usable access.

Record login state when known, capture time, personalization risk, visible-data limits, and inaccessible surfaces. Never call public-web material a live in-platform sample. Never reconstruct missing comments, autocomplete terms, dates, or engagement figures.

### 3. Build a query matrix

Expand seeds across six lenses:

1. identity or role;
2. triggering scene;
3. surface problem;
4. emotion or consequence;
5. workaround or failed solution;
6. desired result or transition.

Collect platform search terms and autocomplete terms only when directly visible. Preserve exact wording and source IDs.

### 4. Sample current content and questions

Collect recent high-interaction content relative to each query snapshot, relevant benchmark-account content, and meaningful comments. Prefer depth over a large unauditable count. Use the default sufficiency targets in `research-protocol.md`, then report actual counts and gaps.

Create a source ledger before interpreting. Assign stable IDs such as `SRC-XHS-001`, `Q-001`, and `CLM-001`.

### 5. Atomize observations

Separate:

- exact user wording;
- explicit questions;
- scenes and triggers;
- emotions;
- time, money, relationship, opportunity, cognitive, and identity costs;
- current workarounds;
- stated desires;
- inferred functional, emotional, and social jobs.
- creator/teacher claims about algorithms, viral standards, income, or performance thresholds.

Keep a short quote exact. Do not silently clean grammar or merge multiple users into a fabricated quote. Anonymize ordinary users unless identity is necessary and already public.

Tag creator/teacher statements as `source_claim`. Preserve speaker, date, locator, claimed scope, and caveat. They may supply language or a test hypothesis, but cannot by themselves establish platform fact, user demand, causality, typical income, or a universal hit standard.

### 6. Synthesize without collapsing evidence types

Label every consequential claim as exactly one of:

- `fact`: directly observed in a cited source;
- `inference`: reasoned from cited facts;
- `hypothesis`: testable but not demonstrated;
- `unknown`: necessary information is absent.

Also assign an independent evidence grade from `A` to `D` or `U`. Do not promote repeated low-quality material into high-grade evidence.

Distinguish:

- high-frequency versus high-value problems;
- short-term heat versus long-term stable demand;
- the stated problem versus the job the user is trying to complete;
- the same problem across different scenes;
- audience relevance versus creator proof and right-to-respond.

### 7. Test creator fit

For each important problem, map the creator's lived experience, demonstrated result, repeated delivery, artifacts/process, payment evidence, constraints, and missing proof. Rate relevance `high`, `medium`, or `low`; rate creator response readiness `proven`, `plausible`, `weak`, or `unknown`.

Do not infer capability from biography, empathy, views, or an attractive positioning sentence alone.

### 8. Produce the standard package

Create both:

- `<slug>-audience-insights.md` using the report template;
- `<slug>-audience-insights.json` conforming to the canonical schema.

The Markdown must include sample scope, user verbatims, questions, scenes, emotions/costs/jobs, before-after map, frequency-value distinction, heat-horizon distinction, evidence grades, creator fit, claims ledger, and unknowns.

The JSON is the downstream source of truth. Markdown may explain more but must not contradict it.

### 9. Validate

Run:

```bash
python3 scripts/validate_output.py <path-to-audience-insights.json>
```

Fix every error before delivery. Then manually audit five things the script cannot prove:

1. every quote is truly present in its cited source;
2. no public material is described as in-platform live evidence;
3. no engagement snapshot is treated as payment evidence;
4. no inference is written as fact;
5. the unknowns are decision-relevant, not boilerplate.

## Stop conditions

Stop and mark the affected area `unknown` when access, provenance, dates, or quote fidelity cannot be established. A complete research run may legitimately conclude that evidence is insufficient. Completeness means the protocol and boundaries were completed, not that every question received an answer.

## Non-goals

- Do not generate post ideas, titles, hooks, scripts, or a content calendar.
- Do not rank a whole platform from a personalized or small convenience sample.
- Do not equate likes, saves, or comments with willingness to pay.
- Do not claim a need is long-term from one short time window.
- Do not publish, message users, or collect private data without authorization.
