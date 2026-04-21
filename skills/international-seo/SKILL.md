---
description: Validates hreflang tags and international SEO configuration. Use when user asks about international SEO, hreflang implementation, multilingual sites, country targeting, or global search indexing.
---

Use `analyze_page_seo` and `international_seo` MCP tools on the provided URL.

Check and report:
- HTML `lang` attribute: present, correct BCP-47 format
- hreflang tags: all alternate language/region variants declared
- Self-referencing hreflang: present for each URL
- x-default hreflang: present for language selector page
- Consistency: all hreflang URLs return 200, reciprocal tags verified
- Canonical conflicts: hreflang vs canonical disagreements

Output: PASS / WARN / FAIL per check + corrected hreflang implementation code block.
