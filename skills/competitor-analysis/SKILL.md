---
description: Runs competitor gap analysis against top-ranking pages. Use when user asks why competitors rank higher, wants to outrank competition, or requests a SERP gap analysis for a keyword.
---

Run a competitor gap analysis using `search_serp`, `analyze_page_seo`, and `compare_with_competitors` MCP tools.

Steps:
1. Find top 3 organic results for the target keyword via `search_serp`
2. Crawl each competitor URL via `analyze_page_seo`
3. Compare against user's page via `compare_with_competitors`

Output comparison table:
- Word count: user vs competitors
- Schema types: user vs competitors
- Heading depth: user vs competitors
- Image count: user vs competitors
- Meta optimization score: user vs competitors

Top gaps sorted by ranking impact — what competitors have that the user's page lacks.
