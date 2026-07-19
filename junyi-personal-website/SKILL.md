---
name: junyi-personal-website
description: Plan, build, review, and prepare deployment of an original personal, expert, creator, portfolio, brand, or service website with a file-capable coding agent such as Codex or Claude Code. Use when a user wants to make or rebuild a 个人官网、品牌官网、IP 主页、作品集、服务落地页, decide between a static site and an application, turn positioning and real proof into a conversion path, inspect responsive screenshots, or publish through Netlify, Vercel, or GitHub Pages. Do not use for a web product whose requirements are already fully specified and unrelated to a personal brand.
---

# Build a Personal Website with AI

Turn positioning and real evidence into an original, maintainable website. The coding agent handles files and checks; the user decides positioning, truth, taste, permissions, and publication.

## Operating rules

1. Work inside a dedicated project directory. Inspect existing files before changing them and preserve unrelated work.
2. Separate `confirmed`, `inferred`, `hypothesis`, and `missing`. Never invent credentials, testimonials, client results, statistics, partnerships, media mentions, or personal stories.
3. Design from the user's brand attributes and references, not by pixel-copying another site or mimicking a named creator's distinctive expression.
4. Make one coherent batch at a time, then render and inspect it at mobile, tablet, and desktop widths. Do not accept “implemented” as visual proof.
5. Keep a reversible local version before material redesigns. Never deploy, buy a domain, change DNS, publish a repository, or add a paid service without explicit user confirmation.
6. Never put API keys, passwords, private tokens, private documents, hidden contact data, or secrets in browser-delivered files or the repository.

## Read the required references

- Read [technical-decision.md](references/technical-decision.md) before choosing a stack.
- Read [content-and-conversion.md](references/content-and-conversion.md) before writing the information architecture or copy.
- Read [design-and-quality.md](references/design-and-quality.md) before implementation and every visual review.
- Read [deployment.md](references/deployment.md) only when preparing or performing deployment.
- Start from [website-brief.template.md](assets/website-brief.template.md); fill missing fields rather than deleting them.

## Workflow

### 1. Establish the website contract

Inspect supplied positioning, voice, offer, evidence, current site, brand assets, analytics, and legal/privacy constraints before asking questions.

If the workspace contains the creator's current `IP战略书.md`, read `B00`, `B02`, `B06`, `B07`, `B08`, and `B09`. They provide the official positioning, real assets, content lines, proof, commercial path, and boundaries. This skill owns that chapter map; do not request a separate simplified positioning file.

Fill the brief with:

- primary visitor, trigger situation, and cold/warm entry source;
- one primary visitor action and any necessary utility action;
- promise, proof, offer, objections, and exclusions;
- required pages and content owners;
- available photos, logos, artifacts, testimonials, permissions, and missing proof;
- maintenance owner, expected change frequency, deadline, budget, domain, hosting, analytics, form, and privacy needs;
- accessibility, language, region, and regulatory constraints.

Ask one material question at a time. Do not start code while the visitor, primary action, or truth boundary is unresolved.

### 2. Choose the smallest suitable technical route

Apply [technical-decision.md](references/technical-decision.md). Default to a static site when pages are public, content changes through files, and actions can be links or third-party forms. Use a static generator or content layer when repeatable content and editorial maintenance justify it. Use an application stack only when the product truly requires accounts, private/personalized data, a database, server-side business logic, or authenticated workflows.

Write a decision record containing:

- chosen route and why it meets the actual requirements;
- rejected alternatives and the requirement that would make each necessary;
- local run/build command, output directory, deployment target, and maintenance path;
- external services, data collected, ownership, cost/plan assumptions, and unresolved risks.

Do not call a framework “more professional” or a static site “always best.” Complexity must be earned by a requirement.

### 3. Design the conversion path before pages

Use [content-and-conversion.md](references/content-and-conversion.md) to define:

`entry context -> recognition -> useful change -> credibility -> offer or next step -> primary action`

Create a page inventory and give every page one job. For the homepage, choose modules based on visitor questions rather than copying a fixed formula. Usually cover:

- a first screen that says who this is for, what change is offered, and the primary action;
- recognizable situations or costs;
- the method, service, work, or resources;
- evidence with source and permission status;
- the person's relevant story or point of view;
- fit, non-fit, boundaries, and frequently asked questions;
- a repeated but non-coercive primary action.

Keep proof placeholders visibly unpublished until the user supplies evidence. Never fabricate social proof “for layout.”

### 4. Create an original design system

Define brand attributes first, then create two or three materially different directions using tokens for color, type, spacing, radius, border, shadow, and motion. Present a small style tile or first-screen prototype; let the user choose before expanding the site.

Meet the quality rules in [design-and-quality.md](references/design-and-quality.md): readable contrast, visible focus, keyboard access, semantic structure, reduced-motion support, responsive images, useful alt text, and mobile-first interaction sizes. Prefer system fonts when simplicity and performance matter; use licensed web fonts only when the brand value justifies the dependency.

### 5. Implement in reviewable slices

For a simple static route, use predictable entry files such as `index.html`, `styles.css`, and an optional `script.js`. Use `index.html` at the published root. For other routes, follow the chosen tool's conventions and document the build output.

Implement in this order:

1. semantic shell, tokens, navigation, footer, and metadata;
2. first screen and one representative content module;
3. remaining homepage modules;
4. detail pages and shared components;
5. forms, analytics, external embeds, and optional enhancements;
6. error/empty states and a useful `404` page where supported.

After every slice:

- run the local site;
- inspect mobile, tablet, and desktop screenshots;
- test navigation, primary action, focus order, overflow, image crops, and long Chinese/English text;
- report what changed, what is still placeholder, and what the user should judge.

### 6. Validate truth, usability, and technical quality

For static HTML, run:

```bash
python3 scripts/validate_static_site.py /absolute/path/to/site
```

Also perform browser-based checks that a parser cannot prove:

- all page routes, downloads, contact methods, QR codes, and external links work;
- the primary action is clear without coercive urgency;
- every result, quote, number, logo, and photo has a source and publication permission;
- mobile, tablet, and desktop layouts have no clipping or horizontal scroll;
- keyboard navigation, visible focus, headings, labels, contrast, reduced motion, and zoom remain usable;
- title, description, canonical URL, favicon, Open Graph image/text, language, and share preview are correct;
- images are appropriately sized/compressed and layout does not jump unnecessarily;
- forms show success, failure, privacy purpose, and ownership of submitted data;
- no secret, private path, staging text, broken asset, console error, or test account remains;
- analytics and consent behavior match the user's region and actual setup.

Do not claim accessibility, SEO, performance, or conversion is “done” merely because the checklist passes. Record tested surfaces, tools, dates, and remaining unknowns.

### 7. Prepare deployment, then ask for confirmation

Read [deployment.md](references/deployment.md). Recommend a route from actual needs and current official documentation:

- manual Netlify deployment for a simple local static folder and low-frequency updates;
- Git-connected Netlify or Vercel for preview/production workflows and automatic deploys;
- GitHub Pages for a public static repository or an eligible paid/private setup where its constraints fit.

Before any external action, show the target repository visibility, host, project/site name, production branch, build command, output directory, domain/DNS changes, data services, expected plan/cost, and rollback path. Obtain explicit confirmation.

After deployment, verify the production URL independently, then test HTTPS, canonical host redirects, custom domain, sharing metadata, forms, analytics, mobile layout, and rollback. Record the deployment date and the exact maintenance workflow; never promise a universal propagation time or perpetual free plan.

## Deliverables

Return or maintain:

1. `website-brief.md` with facts, assumptions, missing assets, and permissions;
2. the technical decision record;
3. page inventory, conversion path, and approved design direction;
4. runnable source files and setup instructions;
5. screenshot review notes for three viewport classes;
6. validation report with blockers and non-blocking gaps;
7. deployment record only after publication is authorized.

End with one of three honest states: `ready_for_content`, `ready_for_deployment`, or `published_and_verified`. Name the evidence required to advance.
