---
description: Competitor gap analysis against top-ranking pages for a keyword. Usage: /seo-intelligence:competitor-gap <url> <keyword>
---

Run competitor gap analysis using `search_serp`, `analyze_page_seo`, and `compare_with_competitors` MCP tools.

Arguments: $ARGUMENTS (format: <url> <keyword>)

Steps:
1. Crawl and score the provided URL
2. Find top 3 organic results for the keyword via `search_serp`
3. Crawl each competitor URL
4. Generate gap analysis via `compare_with_competitors`

Output comparison table: word count, schema types, heading depth, image count, meta scores.
Highlight top gaps sorted by ranking impact with specific fix instructions.
