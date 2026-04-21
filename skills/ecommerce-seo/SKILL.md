---
description: Audits e-commerce product page SEO and validates Product schema. Use when user asks about product page SEO, Google Merchant Center rich results, WooCommerce SEO, Shopify SEO, or Product JSON-LD validation.
---

Use `analyze_page_seo` and `ecommerce_product_seo` MCP tools on the product URL.

Validate JSON-LD Product schema against Google Merchant Center requirements:
- Required: name, image, description, sku, offers (price, currency, availability)
- Recommended: brand, aggregateRating, review
- Flags: missing price, missing availability, no rating markup

Also check: product title SEO, meta description, image alt text, breadcrumb schema, related products internal linking.

Output: validation report + corrected Product JSON-LD block.
