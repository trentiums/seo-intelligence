---
description: Clusters keywords by SERP overlap and classifies search intent. Use when user provides a keyword list and asks about keyword strategy, intent, difficulty, clustering, or cannibalization.
---

Use `cluster_keywords` and `classify_search_intent` MCP tools on the provided keyword list.

Output:
- Intent per keyword: informational / navigational / transactional / commercial (with confidence score)
- Keyword clusters grouped by SERP URL overlap
- Recommended target page per cluster
- Cannibalization warnings: multiple pages competing for same keyword (with severity and fix)
- Difficulty estimate (0-100) with ranking timeline projection per keyword
