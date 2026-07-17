---
name: find-xiaohongshu-benchmarks
description: Broadly discover, then verify, tier, score, and select Xiaohongshu benchmark accounts, specialist references, and post-level breakout specimens from a creator's positioning, audience, content system, capabilities, and monetization path. Use when users ask to find 小红书对标账号、竞品账号、同赛道账号、低粉爆款素人、大中小号分层样本、内容/人设/转化参考账号，compare user-supplied accounts, or want a reproducible candidate pool and shortlist rather than a popularity list.
---

# Find Xiaohongshu Benchmarks

Select accounts that answer specific strategic questions. Do not treat “benchmark” as “admired large creator” or recommend one account for wholesale imitation. Keep discovery broad and evaluation strict: maximize recall in paths 1–5, then apply buyer, repeatability, and commercial-fit filters in path 6.

## Required references

Read before research:

- [research-protocol.md](references/research-protocol.md) for live-search and evidence collection.
- [scorecard.md](references/scorecard.md) for gates, weights, and caps.
- [report-template.md](references/report-template.md) for the deliverable.

Read [source-synthesis.md](references/source-synthesis.md) when explaining how this method incorporates the user's “个人IP打造与低粉高变现” notes or when revising the method.

## Workflow

### 1. Build the benchmark brief

Extract or infer:

- recall trigger: when should which audience remember the creator;
- reach audience and paying buyer;
- promised transformation and commercial anchor;
- three to five content branches and their jobs;
- preferred formats, production capacity, privacy and ethical constraints;
- current account size or stage;
- products and intended conversion path.

Inspect user-provided positioning files before asking questions. Label consequential fields as `fact`, `inference`, `hypothesis`, or `unknown`. If the positioning is broad, research separate lanes rather than inventing a single exact competitor.

### 2. Build a search matrix

Create keyword pools for audience identity, recurring scene/problem, desired change, creator mechanism, content format, and offer. Search combinations, not only category nouns. Include natural user language from existing audience research where available.

Build two kinds of search lanes:

- **trunk lanes** for the paying buyer, costly problem, promised change, and commercial mechanism;
- **branch lanes** for every intended content branch, including identity, life-stage, emotion, worldview, story, format, and adjacent post-level themes.

Run at least two distinct query combinations for every content branch when platform access permits. Do not require an account name or bio to contain the positioning keywords. A creator may be adjacent through one recurring series or one unusually relevant post even when the rest of the account belongs to another category.

Run the six-path search loop in [research-protocol.md](references/research-protocol.md):

1. scan platform topic pages;
2. search by target-audience identity;
3. search by real problem or lived question;
4. search by content mechanism;
5. expand outward from seed-account fingerprints;
6. verify candidates through their recent profiles and comments.

Treat paths 1–5 as discovery and path 6 as verification. During discovery, record rather than reject accounts that match at least one strategic role. Do not use buyer mismatch, lack of repeatability, or a weak commercial path to suppress discovery; use those facts later to classify the account as core, specialist, post-level specimen, or reject. Do not let generic category searches such as `AI博主` define the candidate pool. Select three to five core keywords from the benchmark brief. For each core keyword, enter at least one relevant Xiaohongshu topic page, inspect both popular and latest views, and scan 30–50 posts before tracing repeated authors back to their profiles. If fewer than 30 posts are visible or platform access blocks the scan, inspect all available posts and disclose the shortfall.

When the user supplies a seed account, inspect it first. Extract its audience state, creator identity, recurring topics, content formats, creator temperament, proof system, and monetization path. Creator temperament includes expression style, emotional energy, values and decision style, lifestyle texture, and narrative stance. Expand outward through each fingerprint rather than searching only the account name. Keep the seed in the discovery ledger unless evidence shows it is the wrong identity; do not automatically give it a high score. Audit every user-supplied account even when it arrives after an initial shortlist, and explain whether prior research found it, reasonably rejected it, or missed it because of search coverage.

### 3. Establish a live candidate pool

Use current Xiaohongshu search and profile evidence whenever claiming current benchmarks. Search-engine snippets may help discovery but cannot replace profile inspection.

Maintain two separate sets:

- a **discovery ledger** containing every plausibly useful author or post and the query, branch, or seed fingerprint that surfaced it;
- a **verified pool** containing accounts that have completed enough profile or post-level verification to support a role decision.

When access permits, discover at least 25 plausible authors before narrowing to a verified 15-account pool. Fifteen accounts are a deliverable floor, not a stopping rule. Do not stop until all content branches have been searched and two consecutive, distinct discovery runs produce no new plausibly useful authors. If access prevents saturation, disclose which lanes remain incomplete.

Build three scale tiers with at least five verified accounts each:

1. **Large accounts**: study category-scale themes, blockbuster families, IP narrative, trust architecture, and monetization systems. Do not assume their production conditions are reproducible.
2. **Medium accounts**: study recurring topic systems, serial formats, cadence, stable performance, and content-to-offer alignment. Treat this as the primary operational-learning tier.
3. **Small accounts**: study recent low-resource breakouts, emerging audience language, simple formats, and early positioning. Discount single-post outliers.

Use working follower bands only as a sampling aid, not as a quality claim. Default to `large ≥ 500k`, `medium 50k–499k`, and `small < 50k`; adjust them when the niche is unusually large or sparse and disclose the change.

Within and across the three scale tiers, cover these roles:

1. **Direct benchmark**: similar audience, problem, promise, and business direction.
2. **Recent breakout**: a relatively small account with a strong post or series in roughly the last 15–30 days.
3. **One-stage-ahead benchmark**: mature enough to show repeatable content, but still operationally comparable.
4. **Trust/story benchmark**: unusually strong shared-human or capability trust.
5. **Conversion benchmark**: a visible offer, case system, or conversion path aligned with the creator's intended model.
6. **Specialist benchmark**: a transferable topic, hook, series, format, visual, trust, or conversion asset despite broader audience or business mismatch.
7. **Post-level specimen**: one recent post with unusually relevant framing or audience language, without enough repeatability to treat the whole account as a benchmark.

Role overlap is allowed. Do not force a weak account merely to fill a cell; label an unfilled cell and continue discovery.

### 4. Inspect profiles and comments

For each serious candidate, inspect the profile and a recent sample of posts. Prefer 20–30 posts; if the interface or time does not permit, disclose the smaller sample.

Record:

- profile URL, account name/ID, follower snapshot and observation date;
- bio, category promise, target audience, recurring formats, and update activity;
- recent representative posts, dates, visible interactions, and repeated series;
- whether performance is distributed or depends on one outlier;
- high-signal comment questions, objections, self-descriptions, and buying questions;
- proof, product, consultation, shop, live, community, or private-domain signals;
- resources or identity advantages the user cannot reproduce.

For post-level specimens and specialist candidates, inspect the triggering post and its comments even when the whole account will not enter the core shortlist. Treat comments as audience-language evidence, not verified facts. Never infer income or payment from likes, followers, or a service link.

### 5. Run gates and score

Apply [scorecard.md](references/scorecard.md) only after discovery. Direct benchmarks must pass audience/problem match, current evidence, repeatable content, and operational replicability. Classify narrow assets as specialist benchmarks or post-level specimens instead of inflating or discarding the whole account. Use `scripts/score_candidates.py` when a structured JSON candidate file exists; set `role_scope` to `core`, `specialist`, or `post_specimen`.

Score two separate questions:

- **strategic relevance**: is this account genuinely adjacent to the user's positioning and business;
- **tier learning value**: is it useful for the job assigned to a large, medium, or small account.

Also score **creator-temperament fit** separately when the user has named a seed account or expressed a strong style preference. A strategically adjacent account can still be a poor embodiment benchmark when its voice, emotional energy, values, lifestyle texture, or teacher/peer stance is wrong for the user.

Do not compare a small recent-breakout account with a large mature IP on one undifferentiated ranking. Do not average strategic relevance, tier learning value, and temperament fit into one opaque master score.

Keep separate judgments for:

- attention evidence;
- shared-human trust;
- capability trust;
- commercial signals;
- verified payment evidence.

Public profiles rarely prove payment. Mark it `unknown` unless documented evidence exists.

### 6. Deliver the tiered pool and shortlist

Deliver the 5-large / 5-medium / 5-small candidate pool first. For each account, state the specific asset to study: blockbuster family, topic system, hook, series, story, visual packaging, proof, or conversion.

Then select a smaller execution portfolio when useful, normally:

- two direct benchmarks;
- one recent-breakout or one-stage-ahead benchmark;
- one trust/story benchmark;
- one conversion benchmark.

For every selection, state:

- what strategic question it answers;
- what to learn;
- what not to copy;
- evidence strength and remaining unknowns.

Reject impressive accounts when their audience, production conditions, identity advantage, or business model is materially mismatched.

Reconcile user-supplied accounts against the research output. A strong method should either surface them in the discovery ledger or show, with evidence, why they were excluded. Treat an unexplained omission as a search-recall gap and state which query lane or stopping rule failed.

### 7. Turn observation into tests

Translate each selected benchmark into a hypothesis for the user's own account. Design at least three controlled content tests before judging a structure. Borrow problem framing, information architecture, proof patterns, and series logic; do not copy scripts, distinctive phrasing, stories, thumbnails, or creative assets.

## Research integrity

- Date every platform observation; counts change.
- Distinguish visible facts from inference.
- Do not claim whole-platform rankings from a search sample.
- Do not treat one viral post as repeatability.
- Do not treat follower count as customer quality.
- Do not confuse discovery recall with final fit. A useful research process may discover and then reject an account; it should not silently omit adjacent specialist or post-level evidence.
- Do not publish, follow, message, buy, or contact accounts without user authorization.
- Treat exact algorithm weights, ideal content ratios, and universal posting rules as hypotheses unless supported by current platform documentation or the user's own controlled data.

## Quality bar

Deliver a structured research asset, not a popularity directory. Include the six-path search scope, branch-lane coverage, topic-page coverage and scan counts, discovery-ledger size, saturation status, 5-large / 5-medium / 5-small verified pool, specialist and post-level specimens, user-supplied-account reconciliation, score and gate results, an optional execution shortlist, evidence gaps, and concrete tests for the user's account. If live platform access is blocked, say so and return only a provisional discovery list, never a “verified benchmark” list.
