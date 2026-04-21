---
description: Cluster keywords by SERP overlap and detect cannibalization. Usage: /seo-intelligence:keyword-cluster <keyword1>, <keyword2>, ...
---

Cluster and classify keywords using `cluster_keywords` and `classify_search_intent` MCP tools.

Arguments: $ARGUMENTS (format: comma-separated keyword list)

Output:
- Intent per keyword: informational / navigational / transactional / commercial
- Clusters grouped by SERP URL overlap with recommended target page per cluster
- Cannibalization warnings: severity (high/medium/low) + fix recommendation
- Difficulty estimate (0-100) per keyword with ranking timeline
