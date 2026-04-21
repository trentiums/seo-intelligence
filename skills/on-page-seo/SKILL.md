---
description: Analyzes on-page SEO health for any URL. Use when user mentions a URL and asks about SEO score, title tags, meta descriptions, heading structure, image alt text, or on-page optimization.
---

Run a complete on-page SEO analysis using the `analyze_page_seo` MCP tool on the provided URL.

Return:
- SEO score (0-100)
- Title: length, keyword presence, issues
- Meta description: length, keyword presence, CTA
- Headings: H1 count, hierarchy issues, keyword usage
- Images: alt text coverage percentage
- Links: internal count, external count
- Schema markup types detected
- Top 3 quick wins (easiest fixes, highest impact)

Format as scored report with PASS / WARN / FAIL per section.
