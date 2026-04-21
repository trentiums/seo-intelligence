---
description: Comprehensive multi-keyword SEO audit with competitor analysis and overall site score. Usage: /seo-intelligence:seo-audit <url> <keyword1>, <keyword2>, ...
---

Run a full multi-keyword SEO audit using `analyze_page_seo`, `search_serp`, `compare_with_competitors`, and `generate_ranking_plan` MCP tools.

Arguments: $ARGUMENTS (format: <url> <comma-separated keywords>)

For each keyword:
1. Analyze the URL
2. Find top 3 competitors via SERP
3. Run gap analysis
4. Generate ranking plan

Final output:
- Overall SEO score (weighted average across keywords)
- Per-keyword: competitor comparison, gap analysis, ranking plan
- Cannibalization check across all keywords
- Priority action list: top 10 fixes by ROI across all keywords
