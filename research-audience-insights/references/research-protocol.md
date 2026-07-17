# Research protocol

## Contents

1. Research contract
2. Access and source ledger
3. Sampling
4. Evidence labels and grades
5. Atomic coding
6. Synthesis tests
7. Creator fit
8. Safety and integrity

## 1. Research contract

Translate the request into:

- `audience_situation`: recurring moment, role, constraints, current behavior;
- `research_questions`: one to three questions that can be answered with evidence;
- `decision_context`: what business decision this research informs;
- `creator_claims_to_test`: positioning or capability claims that must not be assumed;
- `time_window`: explicit start/end or a relative window resolved to dates.

Keep reach audience and likely buyer separate when evidence permits.

## 2. Access and source ledger

Create the source ledger before analysis. For every source record:

| Field | Rule |
|---|---|
| `source_id` | Stable and unique. |
| `platform` | Platform or artifact origin. |
| `source_type` | Search suggestion, search result, post, comment, profile, creator first-party, creator/teacher source claim, transaction, interview, public report, or external article. |
| `access_mode` | `in_platform_live`, `public_web`, `user_supplied`, or `unavailable`. |
| `captured_at` | ISO 8601 timestamp or `unknown`. |
| `published_at` | Record when visible; never infer. |
| `url_or_artifact` | Direct URL or an identifiable supplied artifact path/name. |
| `author_scope` | Ordinary user, creator, brand, expert, platform, media, or unknown. |
| `metrics_snapshot` | Only visible metrics plus capture time. |
| `provenance_note` | Login state, screenshot/export/report, personalization, truncation, or other caveat. |

When a supplied report says it used in-platform access, describe the new run as `user_supplied`, not `in_platform_live`. The report may preserve its original method in `provenance_note`.

## 3. Sampling

Use purposeful, diversified sampling. Default targets are diagnostic, not universal truth:

- at least 5 query variants per platform across the six query lenses;
- at least 20 relevant content items per platform when accessible;
- deep-read at least 5 recent or high-interaction items per platform;
- inspect meaningful comments across at least 3 relevant items or accounts;
- aim for 30 distinct, relevant user statements or questions before calling a pattern high-frequency;
- include at least 2 contrasting scenes for an important problem;
- include older comparison material when classifying a need as long-term.

If targets are impossible, continue with the available sample and mark confidence and gaps. Deduplicate copied posts, creator replies, repeated spam, and identical syndicated text. Do not count one user's thread as many independent users without noting it.

Define “high interaction” relative to the captured query/account snapshot. Record the selection rule. Do not call a note “viral” or platform-wide “top” without the required platform-level evidence.

## 4. Evidence labels and grades

### Claim status

- `fact`: directly visible or documented in cited sources.
- `inference`: a synthesis or interpretation supported by cited facts.
- `hypothesis`: a falsifiable possibility needing a designed test.
- `unknown`: information needed for the decision but not available.

### Evidence grade

- `A`: direct first-party behavior/outcome/payment or current auditable primary-platform observation with clear provenance.
- `B`: supplied primary artifact, direct user statement, interview, comment, or creator-owned record with identifiable provenance but not independently re-observed in the current run.
- `C`: public primary page or credible external report suitable for context, not a substitute for internal platform or customer evidence.
- `D`: weak secondary summary, unclear sampling, anecdote, or indirect signal.
- `U`: unverified or unknown.

Grade source strength, not how much the analyst likes the conclusion. An inference based on A sources remains an `inference`, though its evidence grade may be A.

For commercial validation, use this hierarchy:

1. repeat purchase, retention, referral, or documented outcome;
2. payment/deposit for the proposed result;
3. qualified inquiry or direct buying question;
4. detailed private message, interview, or comment describing the problem;
5. follow/repeat viewing/profile visit;
6. share/save/meaningful comment;
7. completion/click/read depth;
8. view/impression/like;
9. stated preference or creator intuition.

Lower levels can support attention or language, not willingness to pay.

## 5. Atomic coding

Code one observation per record.

### Verbatim

Preserve a short exact excerpt. Include source ID, speaker scope, context, and whether it is a post, comment, interview, or supplied report excerpt. Never synthesize a “typical quote.”

### Question

Record explicit questions separately from analyst-rewritten questions. Use `question_kind`: `explicit` or `normalized`.

### Scene

Capture:

- trigger/event;
- time/place/channel;
- people or systems involved;
- current behavior/workaround;
- blocker;
- consequence;
- linked verbatim and source IDs.

### Cost

Use one or more types: `time`, `money`, `opportunity`, `relationship`, `cognitive`, `emotional`, `identity`, `health`, `risk`, `unknown`.

### Job

Separate:

- `surface_problem`: what the user says is wrong;
- `functional_job`: what progress they need in the world;
- `emotional_job`: how they want to feel;
- `social_job`: how they want to be seen or relate to others;
- `success_state`: observable completion condition;
- `job_status`: `stated`, `inferred`, `hypothesized`, or `unknown`.

## 6. Synthesis tests

### Frequency versus value

Estimate frequency only inside the sample and show numerator/denominator when possible. Rate value separately using:

- severity and recurrence;
- decision/relationship/financial cost;
- failed workarounds;
- urgency or costly commitment;
- proximity to the business question;
- creator proof and delivery fit.

Use `high-frequency`, `medium-frequency`, `low-frequency`, or `insufficient-sample`; and independently `high-value`, `medium-value`, `low-value`, or `unknown-value`.

### Short-term heat versus long-term need

Use:

- `short_term_hot`: concentrated in the recent window or tied to a release, event, meme, policy, season, or sudden vocabulary;
- `long_term_stable`: repeats across materially different periods and scenes with stable underlying progress sought;
- `mixed`: durable need with a temporary vocabulary or event spike;
- `insufficient_history`: only one period or inadequate comparison.

Search volume or recent engagement alone cannot prove long-term stability.

### Creator/teacher source claims

Preserve speaker, date, locator, exact scope, and whether the statement reports experience, interpretation, revenue, algorithm behavior, or a performance threshold. Use it as a hypothesis unless current official, auditable platform, transaction, or account-level evidence verifies the exact claim. Repetition across creators is not independent platform proof when they may share the same source.

### Stated problem versus job

Ask: “If the stated problem disappeared, what progress would the user be able to make?” Test the answer against scenes and consequences. Mark it as inference unless the user stated it directly.

### Same problem across scenes

Do not merge scene variants too early. Compare trigger, actor, workaround, cost, and desired outcome. A repeated phrase with different consequences may represent different jobs; different phrases with the same progress may represent one job.

### Before-after map

Describe `before_state`, `trigger_or_barrier`, `desired_after_state`, `success_signal`, and `evidence`. Avoid vague transformations such as “be better” or “grow.”

## 7. Creator fit

For every high-value or strategically important problem, check:

- lived crossing: creator has personally experienced the before and after;
- demonstrated outcome: verifiable personal or client result;
- repeated delivery: multiple cases, retention, referral, or recurring use;
- process/artifact: visible method, workflow, dataset, product, or demonstration;
- payment adjacency: payment or a plausible minimum test for this result;
- ethical/identity fit: privacy, boundaries, desired business, and audience;
- missing proof: what would change confidence.

Rate `relevance` separately from `response_readiness`. Shared-human trust does not equal capability trust.

## 8. Safety and integrity

- Collect only material available through authorized access.
- Do not bypass login, anti-bot controls, rate limits, or privacy settings.
- Anonymize ordinary users and avoid unnecessary personal data.
- Do not infer income, diagnosis, family status, or purchase intent from lifestyle content.
- Keep short quotes; link or cite the source rather than reproducing long content.
- Record personalization and time sensitivity for platform search snapshots.
- Acknowledge missing comment access, hidden counts, deleted content, and inaccessible time-series data.
