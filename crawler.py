"""Page crawling and HTML parsing for SEO analysis."""

import re
import json
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from models import PageAnalysis, HeadingInfo, LinkInfo, ImageInfo, FAQItem


# Browser-like user agent to avoid blocks
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)

# Timeout for page fetches (seconds)
FETCH_TIMEOUT = 30


async def crawl_page(url: str) -> str:
    """Fetch raw HTML from a URL.

    Args:
        url: The URL to crawl.

    Returns:
        Raw HTML string.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=FETCH_TIMEOUT,
        verify=False,
    ) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


def parse_page(html: str, url: str) -> PageAnalysis:
    """Parse HTML into a structured PageAnalysis.

    Args:
        html: Raw HTML string.
        url: The original URL (used for resolving relative links).

    Returns:
        A PageAnalysis dataclass with all extracted SEO data.
    """
    soup = BeautifulSoup(html, "lxml")
    analysis = PageAnalysis(url=url)

    # --- Title ---
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        analysis.title = title_tag.string.strip()

    # --- Meta Description ---
    meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    if meta_desc and meta_desc.get("content"):
        analysis.meta_description = meta_desc["content"].strip()

    # --- Canonical ---
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical and canonical.get("href"):
        analysis.canonical_url = canonical["href"].strip()

    # --- Headings ---
    analysis.headings = _extract_headings(soup)
    analysis.h1_count = sum(1 for h in analysis.headings if h.level == 1)
    analysis.h2_count = sum(1 for h in analysis.headings if h.level == 2)
    analysis.h3_count = sum(1 for h in analysis.headings if h.level == 3)

    # --- Content / Word Count ---
    body = soup.find("body")
    if body:
        # Remove script and style elements
        for tag in body.find_all(["script", "style", "noscript"]):
            tag.decompose()
        text = body.get_text(separator=" ", strip=True)
        analysis.content_text = text
        analysis.word_count = len(text.split())

    # --- Links ---
    analysis.internal_links, analysis.external_links = _extract_links(soup, url)
    analysis.internal_link_count = len(analysis.internal_links)
    analysis.external_link_count = len(analysis.external_links)

    # --- Images ---
    analysis.images = _extract_images(soup)
    analysis.total_images = len(analysis.images)
    analysis.images_with_alt = sum(1 for img in analysis.images if img.has_alt)
    analysis.images_without_alt = analysis.total_images - analysis.images_with_alt
    if analysis.total_images > 0:
        analysis.image_alt_coverage = round(
            (analysis.images_with_alt / analysis.total_images) * 100, 1
        )

    # --- FAQ Detection ---
    analysis.faqs = _extract_faqs(soup)
    analysis.has_faq_section = len(analysis.faqs) > 0

    # --- Schema / Structured Data ---
    analysis.schema_types = _extract_schema_types(soup)
    analysis.has_schema = len(analysis.schema_types) > 0

    # --- Open Graph ---
    analysis.og_title = _get_meta_property(soup, "og:title")
    analysis.og_description = _get_meta_property(soup, "og:description")
    analysis.og_image = _get_meta_property(soup, "og:image")
    analysis.has_og_tags = bool(analysis.og_title or analysis.og_description)

    # --- Technical ---
    viewport = soup.find("meta", attrs={"name": "viewport"})
    analysis.has_viewport_meta = viewport is not None

    html_tag = soup.find("html")
    analysis.has_lang_attribute = bool(html_tag and html_tag.get("lang"))

    charset = soup.find("meta", attrs={"charset": True})
    analysis.has_charset = charset is not None

    return analysis


# ─── Private Helpers ─────────────────────────────────────────────────────────


def _extract_headings(soup: BeautifulSoup) -> list[HeadingInfo]:
    """Extract all headings H1-H6."""
    headings = []
    for level in range(1, 7):
        for tag in soup.find_all(f"h{level}"):
            text = tag.get_text(strip=True)
            if text:
                headings.append(HeadingInfo(level=level, text=text))
    return headings


def _extract_links(
    soup: BeautifulSoup, base_url: str
) -> tuple[list[LinkInfo], list[LinkInfo]]:
    """Extract and classify internal vs external links."""
    internal: list[LinkInfo] = []
    external: list[LinkInfo] = []
    base_domain = urlparse(base_url).netloc.lower()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        text = a_tag.get_text(strip=True)

        # Skip anchors, javascript, mailto
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        link_domain = parsed.netloc.lower()

        link = LinkInfo(url=full_url, text=text, is_internal=(link_domain == base_domain))
        if link.is_internal:
            internal.append(link)
        else:
            external.append(link)

    return internal, external


def _extract_images(soup: BeautifulSoup) -> list[ImageInfo]:
    """Extract image tags and their alt attributes."""
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt", "")
        images.append(ImageInfo(src=src, alt=alt, has_alt=bool(alt.strip())))
    return images


def _extract_faqs(soup: BeautifulSoup) -> list[FAQItem]:
    """Detect FAQ sections via schema markup or common HTML patterns."""
    faqs: list[FAQItem] = []

    # Method 1: Look for FAQPage schema in JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                for item in data:
                    faqs.extend(_parse_faq_schema(item))
            else:
                faqs.extend(_parse_faq_schema(data))
        except (json.JSONDecodeError, TypeError):
            continue

    # Method 2: Look for common FAQ HTML patterns (if no schema found)
    if not faqs:
        # Look for elements with FAQ-related class/id
        faq_containers = soup.find_all(
            attrs={"class": re.compile(r"faq", re.I)}
        ) or soup.find_all(attrs={"id": re.compile(r"faq", re.I)})

        for container in faq_containers:
            # Look for question/answer pairs (dt/dd or heading/paragraph)
            dts = container.find_all("dt")
            dds = container.find_all("dd")
            for dt, dd in zip(dts, dds):
                q = dt.get_text(strip=True)
                a = dd.get_text(strip=True)
                if q and a:
                    faqs.append(FAQItem(question=q, answer=a))

            # Also try heading + sibling paragraph pattern
            if not faqs:
                for heading in container.find_all(re.compile(r"^h[2-4]$")):
                    q = heading.get_text(strip=True)
                    sibling = heading.find_next_sibling(["p", "div"])
                    if sibling:
                        a = sibling.get_text(strip=True)
                        if q and a:
                            faqs.append(FAQItem(question=q, answer=a))

    return faqs


def _parse_faq_schema(data: dict) -> list[FAQItem]:
    """Parse FAQPage schema from JSON-LD data."""
    faqs = []
    schema_type = data.get("@type", "")
    if schema_type == "FAQPage":
        for entity in data.get("mainEntity", []):
            q = entity.get("name", "")
            a_obj = entity.get("acceptedAnswer", {})
            a = a_obj.get("text", "") if isinstance(a_obj, dict) else ""
            if q and a:
                faqs.append(FAQItem(question=q, answer=a))
    return faqs


def _extract_schema_types(soup: BeautifulSoup) -> list[str]:
    """Extract all schema.org types found on the page."""
    types: set[str] = set()

    # JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "@type" in item:
                        types.add(item["@type"])
            elif isinstance(data, dict) and "@type" in data:
                types.add(data["@type"])
        except (json.JSONDecodeError, TypeError):
            continue

    # Microdata
    for tag in soup.find_all(attrs={"itemtype": True}):
        itemtype = tag["itemtype"]
        if "schema.org" in itemtype:
            schema_name = itemtype.rstrip("/").split("/")[-1]
            types.add(schema_name)

    return sorted(types)


def _get_meta_property(soup: BeautifulSoup, property_name: str) -> str:
    """Get content of a meta property tag."""
    tag = soup.find("meta", attrs={"property": property_name})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""


def format_page_analysis(analysis: PageAnalysis) -> str:
    """Format a PageAnalysis into a readable string for Claude."""
    if analysis.error:
        return f"❌ Error analyzing {analysis.url}: {analysis.error}"

    lines = [
        f"# SEO Analysis: {analysis.url}",
        "",
        "## Meta Information",
        f"- **Title**: {analysis.title or '⚠️ MISSING'}",
        f"  - Length: {len(analysis.title)} chars {'✅' if 30 <= len(analysis.title) <= 60 else '⚠️ (recommended: 30-60)'}",
        f"- **Meta Description**: {analysis.meta_description or '⚠️ MISSING'}",
        f"  - Length: {len(analysis.meta_description)} chars {'✅' if 120 <= len(analysis.meta_description) <= 160 else '⚠️ (recommended: 120-160)'}",
        f"- **Canonical URL**: {analysis.canonical_url or '⚠️ MISSING'}",
        f"- **Open Graph Tags**: {'✅ Present' if analysis.has_og_tags else '⚠️ MISSING'}",
        "",
        "## Heading Structure",
        f"- **H1 tags**: {analysis.h1_count} {'✅' if analysis.h1_count == 1 else '⚠️ (should be exactly 1)'}",
        f"- **H2 tags**: {analysis.h2_count}",
        f"- **H3 tags**: {analysis.h3_count}",
        f"- **Total headings**: {len(analysis.headings)}",
    ]

    if analysis.headings:
        lines.append("- **Heading hierarchy**:")
        for h in analysis.headings[:15]:  # Limit display
            indent = "  " * h.level
            lines.append(f"  {indent}H{h.level}: {h.text[:80]}")

    lines.extend([
        "",
        "## Content",
        f"- **Word count**: {analysis.word_count} {'✅' if analysis.word_count >= 300 else '⚠️ (thin content — aim for 800+)'}",
        "",
        "## Links",
        f"- **Internal links**: {analysis.internal_link_count}",
        f"- **External links**: {analysis.external_link_count}",
        "",
        "## Images",
        f"- **Total images**: {analysis.total_images}",
        f"- **With alt text**: {analysis.images_with_alt}",
        f"- **Without alt text**: {analysis.images_without_alt}",
        f"- **Alt coverage**: {analysis.image_alt_coverage}% {'✅' if analysis.image_alt_coverage == 100 else '⚠️'}",
        "",
        "## FAQ",
        f"- **FAQ section detected**: {'✅ Yes' if analysis.has_faq_section else '❌ No'}",
        f"- **FAQ items found**: {len(analysis.faqs)}",
        "",
        "## Schema / Structured Data",
        f"- **Schema present**: {'✅ Yes' if analysis.has_schema else '❌ No'}",
    ])

    if analysis.schema_types:
        lines.append(f"- **Schema types**: {', '.join(analysis.schema_types)}")

    lines.extend([
        "",
        "## Technical",
        f"- **Viewport meta**: {'✅' if analysis.has_viewport_meta else '❌ MISSING'}",
        f"- **Lang attribute**: {'✅' if analysis.has_lang_attribute else '❌ MISSING'}",
        f"- **Charset declaration**: {'✅' if analysis.has_charset else '❌ MISSING'}",
    ])

    return "\n".join(lines)
