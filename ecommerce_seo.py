"""
E-commerce SEO Module.
Handles parsing and validating Product Schema (JSON-LD) for rich snippets.
"""

import json
from crawler import crawl_page, extract_schema_data
from models import ProductSchemaResult, EcommerceSeoReport

async def analyze_product_seo(url: str) -> EcommerceSeoReport:
    """Analyzes a product page's JSON-LD schema for Google Merchant Center / Rich Result compliance."""
    report = EcommerceSeoReport(url=url)
    try:
        html = await crawl_page(url)
    except Exception as e:
        report.error = f"Failed to crawl {url}: {str(e)}"
        return report

    schemas = extract_schema_data(html)
    product_schema = None

    # Find the Product schema
    for schema in schemas:
        schema_type = schema.get("@type", "")
        if schema_type == "Product" or (isinstance(schema_type, list) and "Product" in schema_type):
            product_schema = schema
            break

    if not product_schema:
        report.schema_status = "Missing"
        report.recommendations = "No Product schema found. You must add JSON-LD Product schema to this page to be eligible for Google rich results (showing price, rating, and availability directly in SERP)."
        return report

    result = ProductSchemaResult()
    missing = []

    # Name
    result.name = product_schema.get("name", "")
    if result.name:
        report.product_name = result.name
    else:
        missing.append("name")

    # Offers (Price, Currency, Availability)
    offers = product_schema.get("offers", {})
    if isinstance(offers, list) and len(offers) > 0:
        offers = offers[0] # Take first offer

    if offers:
        result.price = float(offers.get("price", 0.0))
        if not result.price: missing.append("offers.price")
        
        result.currency = offers.get("priceCurrency", "")
        if not result.currency: missing.append("offers.priceCurrency")
        
        result.availability = offers.get("availability", "")
        if not result.availability: missing.append("offers.availability")
    else:
        missing.extend(["offers", "offers.price", "offers.priceCurrency", "offers.availability"])

    # AggregateRating
    ratings = product_schema.get("aggregateRating", {})
    if ratings:
        result.rating = float(ratings.get("ratingValue", 0.0))
        result.review_count = int(ratings.get("reviewCount", 0) or ratings.get("ratingCount", 0))
    else:
        missing.append("aggregateRating")

    # Image
    if not product_schema.get("image"):
        missing.append("image")

    # Description
    if not product_schema.get("description"):
        missing.append("description")

    result.missing_fields = missing
    report.schema_details = result

    # Determine status
    if not missing:
        report.schema_status = "Valid"
        report.recommendations = "Excellent! Your Product schema is complete. You are maximizing your chances for rich snippets in Google Search."
    else:
        report.schema_status = "Incomplete"
        recs = [f"Your Product schema is missing {len(missing)} recommended/required fields: {', '.join(missing)}."]
        if "aggregateRating" in missing:
            recs.append("Adding 'aggregateRating' is critical for showing stars in Google results, which dramatically increases CTR.")
        if "offers" in missing or "offers.price" in missing:
            recs.append("Missing price data prevents your product from showing up in Google Shopping free listings.")
        report.recommendations = " ".join(recs)

    return report

def format_ecommerce_report(report: EcommerceSeoReport) -> str:
    """Format the e-commerce SEO report for Claude."""
    if report.error:
        return f"⚠️ **E-commerce SEO Error:** {report.error}"

    lines = [
        f"## 🛒 E-commerce Product SEO Analysis",
        f"**URL:** `{report.url}`",
    ]
    
    if report.product_name:
         lines.append(f"**Product:** `{report.product_name}`")
         
    status_icon = "❌" if report.schema_status == "Missing" else "⚠️" if report.schema_status == "Incomplete" else "✅"
    lines.append(f"**Schema Status:** {status_icon} {report.schema_status}\n")

    if report.schema_status != "Missing":
        lines.append("### Schema Data Extracted:")
        d = report.schema_details
        price_str = f"{d.price} {d.currency}" if d.price else "Not found"
        avail_str = d.availability.split("/")[-1] if "/" in d.availability else (d.availability or "Not found")
        rating_str = f"⭐ {d.rating} ({d.review_count} reviews)" if d.rating else "Not found"
        
        lines.extend([
            f"- **Price:** {price_str}",
            f"- **Availability:** {avail_str}",
            f"- **Rating:** {rating_str}"
        ])
        
        if d.missing_fields:
            lines.append(f"\n### ⚠️ Missing Fields ({len(d.missing_fields)})")
            for field in d.missing_fields:
                lines.append(f"- `{field}`")

    lines.append(f"\n**Recommendation:** {report.recommendations}")
    return "\n".join(lines)
