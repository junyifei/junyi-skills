# Deployment decision and verification

Current platform facts must be rechecked against official documentation at deployment time.

## Netlify

Use manual drag-and-drop when the source is a small local static folder and updates are infrequent. The published folder needs the finished files; a simple static site should have `index.html` at its root. Manual deployment does not provide the same Git-triggered workflow as a connected repository.

Use Git-connected deployment when preview builds, versioned review, or automatic production updates matter. Confirm repository access, build command, publish directory, production branch, environment variables, and current plan limits.

Official references:

- <https://docs.netlify.com/deploy/create-deploys/>
- <https://docs.netlify.com/manage/domains/get-started-with-domains/>
- <https://docs.netlify.com/manage/domains/secure-domains-with-https/https-ssl/>

## Vercel

Use when the chosen framework or workflow fits Vercel, or when Git-based preview and production deployments are wanted. Confirm framework preset, build command, output directory, environment variables, domain records, and current plan limits in the project settings and official docs.

Official references:

- <https://vercel.com/docs/deployments>
- <https://vercel.com/docs/domains>

## GitHub Pages

Use for a static site when GitHub ownership and repository visibility/plan constraints fit. Verify the publication source, custom domain, domain verification, and HTTPS settings. Do not assume a private repository is eligible on every account plan.

Official references:

- <https://docs.github.com/en/pages/quickstart>
- <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site>

## Pre-deployment record

```markdown
- Host and account owner:
- Repository and visibility:
- Production branch:
- Build command:
- Output/publish directory:
- External services and environment variables:
- Project/site name:
- Production URL:
- Custom domain and exact DNS changes:
- Current plan/cost checked on:
- Rollback route:
- Explicit publication confirmation:
```

## Post-deployment verification

Test the production URL, not only localhost:

- HTTPS and intended canonical host;
- apex/`www` behavior and redirect loops;
- all routes, assets, forms, downloads, contact methods, and QR codes;
- title, description, favicon, Open Graph image/text, and share preview;
- mobile/tablet/desktop layout and keyboard interaction;
- analytics/consent only if actually configured;
- absence of secrets, source maps or logs exposing private information;
- a documented rollback and update workflow.

DNS and deployment timing vary. Report observed state and provider status; never promise a fixed propagation time.
