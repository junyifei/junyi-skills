# Technical decision: static site, content site, or application

Choose from requirements, not fashion.

## Route A: simple static site

Use HTML/CSS and small, optional JavaScript when:

- every page is public;
- content is edited in files by the owner or coding agent;
- the main actions are links, downloads, email/contact links, or a hosted form;
- no private user data, login, database, or server-side workflow is required.

This is usually the smallest route for a personal profile, service page, portfolio, campaign landing page, or small brand site. Prefer a root `index.html`, shared stylesheet, semantic HTML, and minimal dependencies.

## Route B: generated or content-managed static site

Consider a static site generator or a content layer when:

- many repeatable articles, cases, projects, or resources share templates;
- a non-developer must publish regularly;
- content collections, feeds, tags, search indexes, localization, or previews materially reduce maintenance work.

Record who owns the content system and what happens if the service is removed. A few pages do not justify a content platform by themselves.

## Route C: application

Use an application stack only when one or more core requirements need it:

- accounts, authorization, private/personalized pages, or member-only data;
- stored user-generated data or a database;
- server-side business rules, protected secrets, or authenticated third-party APIs;
- transactional workflows that cannot safely be delegated to a hosted checkout/form;
- live state shared across users.

A payment link, newsletter signup, booking link, simple search, or analytics tag alone does not require a custom application.

## Decision record

Write:

```markdown
## Technical decision
- Required capabilities:
- Chosen route:
- Why this is sufficient:
- Rejected route(s):
- Upgrade trigger:
- Local run/build:
- Published output:
- Hosting candidate:
- External services and data:
- Maintenance owner:
- Cost/plan assumptions to verify:
- Risks and unknowns:
```

Do not promise that a platform is free, fastest, or permanent. Verify current official documentation when deployment is in scope.
