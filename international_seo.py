"""
International SEO Module.
Handles parsing and validating hreflang tags and HTML lang attributes for multi-regional/lingual sites.
"""

from bs4 import BeautifulSoup
from crawler import crawl_page
from models import HreflangData, InternationalSeoReport

async def analyze_international_seo(url: str) -> InternationalSeoReport:
    """Audit a webpage for basic International SEO configurations (hreflang, html lang)."""
    report = InternationalSeoReport(url=url)
    try:
        html = await crawl_page(url)
    except Exception as e:
        report.error = f"Failed to crawl {url}: {str(e)}"
        return report

    soup = BeautifulSoup(html, 'html.parser')

    # 1. HTML Lang attribute
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        report.html_lang = html_tag['lang']

    # 2. Extract hreflang links
    hreflang_links = soup.find_all('link', rel='alternate', hreflang=True)
    tags = []

    for link in hreflang_links:
        href = link.get('href', '')
        hreflang_val = link.get('hreflang', '').lower()
        
        if not href or not hreflang_val:
            continue
            
        is_default = (hreflang_val == 'x-default')
        if is_default:
            report.has_x_default = True
            
        # Parse language and region (e.g., 'en', 'en-us')
        parts = hreflang_val.split('-')
        lang = parts[0]
        region = parts[1] if len(parts) > 1 else ""
        
        tag_data = HreflangData(
            url=href,
            language=lang,
            region=region,
            is_x_default=is_default
        )
        tags.append(tag_data)
        
        # Check self-referencing
        # Strip trailing slash or query params for basic exact matching
        clean_url = url.split('?')[0].rstrip('/')
        clean_href = href.split('?')[0].rstrip('/')
        
        if clean_url == clean_href:
            report.has_self_referencing = True

    report.hreflang_tags = tags
    
    # Generate recommendations
    recs = []
    if not report.html_lang:
        recs.append("Missing `<html lang>` attribute. This is the most basic signal for Google and screen readers to know your page's primary language.")
        
    if not tags:
        recs.append("No `hreflang` tags found. If your site targets multiple countries or languages, you need these to prevent duplicate content issues and ensure the right users see the right language.")
    else:
        if not report.has_x_default:
            recs.append("Missing `x-default` hreflang tag. It is highly recommended to provide a fallback URL for users whose language/region does not match any specific hreflang tags.")
            
        if not report.has_self_referencing:
            recs.append("Missing self-referencing `hreflang` tag. The current page must link to itself in the hreflang cluster to be considered valid by Google.")
            
        if report.has_x_default and report.has_self_referencing:
             recs.append("Excellent! Your international SEO tags are well-configured.")
             
    report.recommendations = " ".join(recs)
    return report

def format_international_report(report: InternationalSeoReport) -> str:
    """Format the International SEO report for Claude."""
    if report.error:
        return f"⚠️ **International SEO Error:** {report.error}"

    lines = [
        f"## 🌍 International SEO Analysis",
        f"**URL:** `{report.url}`\n",
    ]
    
    status_icon = "❌" if not report.html_lang else "✅"
    lines.append(f"**Primary Language `<html lang>`:** {status_icon} `{report.html_lang or 'Missing'}`\n")
    
    if report.hreflang_tags:
        lines.append(f"### Found {len(report.hreflang_tags)} `hreflang` Valid Targets:")
        lines.append("| Language | Region | x-default | Target URL |")
        lines.append("|----------|--------|:---------:|------------|")
        
        for t in report.hreflang_tags:
             lang = t.language
             reg = t.region or "-"
             default = "Yes" if t.is_x_default else "-"
             lines.append(f"| `{lang}` | `{reg}` | {default} | `{t.url}` |")
             
        lines.append("\n### Configuration Checks:")
        sr_icon = "✅" if report.has_self_referencing else "❌"
        lines.append(f"- Self-referencing tag present? {sr_icon} {'Yes' if report.has_self_referencing else 'No'}")
        
        xd_icon = "✅" if report.has_x_default else "❌"
        lines.append(f"- Catch-all `x-default` present? {xd_icon} {'Yes' if report.has_x_default else 'No'}")
        
    lines.append(f"\n**Recommendation:** {report.recommendations}")
    return "\n".join(lines)
