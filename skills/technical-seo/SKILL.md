---
description: Runs a technical SEO infrastructure audit. Use when user asks about site crawlability, indexing issues, robots.txt, sitemap, SSL, redirects, canonical tags, or mobile readiness.
---

Run a technical SEO audit using the `technical_seo_audit` MCP tool on the provided URL.

Check and report:
- sitemap.xml: exists, valid, URL count
- robots.txt: exists, disallow rules, sitemap reference
- SSL/HTTPS: enforced, mixed content warnings
- Redirects: chains detected, 301 vs 302
- Canonical tags: self-referencing, conflicting
- Mobile: viewport tag present
- Lang attribute and charset declaration

Each item: PASS / WARN / FAIL with specific fix for every failure.
