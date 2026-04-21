---
description: Generate production-ready JSON-LD schema markup for any page. Usage: /seo-intelligence:generate-schema <url> [schema-type]
---

Generate valid JSON-LD schema markup using the `analyze_page_seo` MCP tool.

Arguments: $ARGUMENTS (format: <url> [Article|Product|LocalBusiness|FAQ|VideoObject|auto])

Auto-detect best schema type from page content if type not specified.

Output:
- Complete JSON-LD block ready to paste into `<head>`
- Validation notes against Google Rich Results requirements
- Missing required fields flagged
- Optional recommended fields listed
- Preview of expected rich result appearance
