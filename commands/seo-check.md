---
description: Quick on-page SEO health check. Usage: /seo-intelligence:seo-check <url> <keyword>
---

Run a complete on-page SEO health check using the `analyze_page_seo` MCP tool.

Arguments: $ARGUMENTS (format: <url> <target-keyword>)

Return:
- SEO score (0-100)
- Title tag: length, keyword presence, issues
- Meta description: length, keyword, CTA
- Heading hierarchy: H1 count, structure issues
- Image alt text coverage
- Internal/external link counts
- Schema markup detected
- Top 5 quick wins sorted by impact

Format as scored report with PASS / WARN / FAIL per section.
