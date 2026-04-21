---
description: Generate an SEO content brief from competitor analysis. Usage: /seo-intelligence:content-brief <keyword>
---

Generate an SEO content brief using `search_serp` and `analyze_page_seo` MCP tools.

Arguments: $ARGUMENTS (format: <target-keyword>)

Crawl top 3 ranking pages for the keyword and produce:
- Recommended title (keyword-rich, under 60 chars)
- Meta description template (150-160 chars)
- Suggested heading structure (H1 → H2s → H3s)
- Target word count (competitor average + 10%)
- People Also Ask questions to answer
- Must-cover topics from competitor analysis
- Recommended schema type
- Content gaps: what top rankers have that others miss
