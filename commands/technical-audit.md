---
description: Full technical SEO infrastructure audit. Usage: /seo-intelligence:technical-audit <url>
---

Run a technical SEO audit using the `technical_seo_audit` MCP tool.

Arguments: $ARGUMENTS (format: <url>)

Check and report PASS / WARN / FAIL for:
- sitemap.xml: exists, valid, URL count
- robots.txt: exists, disallow rules, sitemap reference
- SSL/HTTPS: enforced, mixed content warnings
- Redirects: chains, 301 vs 302
- Canonical tags: self-referencing, conflicting
- Mobile: viewport tag present
- Lang attribute and charset

Include specific fix recommendation for every WARN and FAIL.
