"""Technical SEO audit module.

Performs infrastructure-level SEO checks: sitemap, robots.txt, SSL,
redirects, canonicals, and mobile readiness.
"""

from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup

from models import PageAnalysis, TechnicalCheckResult, TechnicalAuditResult


# Timeout for technical checks (seconds)
CHECK_TIMEOUT = 15

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)


# ─── Main Audit Orchestrator ────────────────────────────────────────────────


async def audit_technical_seo(url: str) -> TechnicalAuditResult:
    """Run a complete technical SEO audit on a URL.

    Performs checks on: sitemap.xml, robots.txt, SSL/HTTPS, redirect chains,
    canonical tags, and mobile readiness.

    Args:
        url: The URL to audit.

    Returns:
        A TechnicalAuditResult with all check results.
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)

    domain_root = f"{parsed.scheme}://{parsed.netloc}"
    result = TechnicalAuditResult(url=url)

    try:
        async with httpx.AsyncClient(
            timeout=CHECK_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        ) as client:
            # Run all checks
            checks = []
            checks.append(await check_sitemap(client, domain_root))
            checks.append(await check_robots_txt(client, domain_root))
            checks.append(await check_ssl(client, url))
            checks.append(await check_redirects(url))
            checks.append(await check_page_basics(client, url))

            result.checks = checks

    except Exception as e:
        result.error = f"Audit failed: {str(e)}"
        return result

    # Tally results
    result.passed = sum(1 for c in result.checks if c.status == "pass")
    result.warnings = sum(1 for c in result.checks if c.status == "warn")
    result.failed = sum(1 for c in result.checks if c.status == "fail")

    if result.failed >= 2:
        result.overall_status = "Critical"
    elif result.failed >= 1 or result.warnings >= 2:
        result.overall_status = "Needs Attention"
    else:
        result.overall_status = "Healthy"

    return result


# ─── Individual Checks ──────────────────────────────────────────────────────


async def check_sitemap(client: httpx.AsyncClient, domain_root: str) -> TechnicalCheckResult:
    """Check for sitemap.xml presence and validity."""
    sitemap_url = f"{domain_root}/sitemap.xml"
    try:
        resp = await client.get(sitemap_url)
        if resp.status_code == 200:
            content = resp.text
            if "<urlset" in content or "<sitemapindex" in content:
                # Count URLs
                url_count = content.count("<url>") + content.count("<loc>")
                return TechnicalCheckResult(
                    check="Sitemap (sitemap.xml)",
                    status="pass",
                    details=f"Valid sitemap found at {sitemap_url} with ~{url_count} URLs.",
                )
            else:
                return TechnicalCheckResult(
                    check="Sitemap (sitemap.xml)",
                    status="warn",
                    details=f"File exists at {sitemap_url} but does not appear to be a valid XML sitemap.",
                    recommendation="Ensure sitemap.xml follows the sitemaps.org protocol with <urlset> or <sitemapindex> root elements.",
                )
        else:
            return TechnicalCheckResult(
                check="Sitemap (sitemap.xml)",
                status="fail",
                details=f"No sitemap found at {sitemap_url} (HTTP {resp.status_code}).",
                recommendation="Create a sitemap.xml and submit it to Google Search Console. Most CMS platforms can auto-generate sitemaps.",
            )
    except Exception as e:
        return TechnicalCheckResult(
            check="Sitemap (sitemap.xml)",
            status="fail",
            details=f"Could not fetch sitemap: {str(e)}",
            recommendation="Ensure sitemap.xml is accessible at the domain root.",
        )


async def check_robots_txt(client: httpx.AsyncClient, domain_root: str) -> TechnicalCheckResult:
    """Check for robots.txt presence and content."""
    robots_url = f"{domain_root}/robots.txt"
    try:
        resp = await client.get(robots_url)
        if resp.status_code == 200:
            content = resp.text.strip()
            issues = []

            # Check for overly restrictive rules
            if "Disallow: /" in content and "Disallow: /\n" not in content.replace("Disallow: / ", ""):
                # Only flag if it's a blanket block (not just "Disallow: /admin")
                lines = content.split("\n")
                for line in lines:
                    stripped = line.strip()
                    if stripped == "Disallow: /":
                        issues.append("⚠️ Blanket 'Disallow: /' blocks all crawlers from the entire site.")

            # Check for sitemap reference
            has_sitemap_ref = "sitemap:" in content.lower()

            if issues:
                return TechnicalCheckResult(
                    check="Robots.txt",
                    status="warn",
                    details=f"robots.txt found but has issues: {'; '.join(issues)}",
                    recommendation="Review robots.txt rules. A blanket 'Disallow: /' prevents search engines from crawling your site.",
                )
            elif not has_sitemap_ref:
                return TechnicalCheckResult(
                    check="Robots.txt",
                    status="warn",
                    details="robots.txt exists but does not reference a sitemap.",
                    recommendation=f"Add 'Sitemap: {domain_root}/sitemap.xml' to robots.txt to help search engines discover your sitemap.",
                )
            else:
                return TechnicalCheckResult(
                    check="Robots.txt",
                    status="pass",
                    details=f"Valid robots.txt found with sitemap reference.",
                )
        else:
            return TechnicalCheckResult(
                check="Robots.txt",
                status="warn",
                details=f"No robots.txt found (HTTP {resp.status_code}). Not critical but recommended.",
                recommendation="Create a robots.txt to guide search engine crawlers. Even a minimal one with a Sitemap directive helps.",
            )
    except Exception as e:
        return TechnicalCheckResult(
            check="Robots.txt",
            status="warn",
            details=f"Could not fetch robots.txt: {str(e)}",
            recommendation="Ensure robots.txt is accessible at the domain root.",
        )


async def check_ssl(client: httpx.AsyncClient, url: str) -> TechnicalCheckResult:
    """Check HTTPS and basic SSL configuration."""
    parsed = urlparse(url)

    if parsed.scheme != "https":
        return TechnicalCheckResult(
            check="SSL / HTTPS",
            status="fail",
            details=f"Site is served over HTTP, not HTTPS.",
            recommendation="Migrate to HTTPS. Install an SSL certificate (free via Let's Encrypt) and redirect all HTTP traffic to HTTPS.",
        )

    try:
        resp = await client.get(url)
        html = resp.text

        # Check for mixed content indicators
        mixed_content_patterns = [
            'src="http://',
            "src='http://",
            'href="http://',
            "href='http://",
        ]
        mixed_count = sum(html.count(p) for p in mixed_content_patterns)

        if mixed_count > 0:
            return TechnicalCheckResult(
                check="SSL / HTTPS",
                status="warn",
                details=f"HTTPS is enabled but {mixed_count} potential mixed content references found (HTTP resources on HTTPS page).",
                recommendation="Update all resource URLs (images, scripts, stylesheets) to use HTTPS or protocol-relative URLs (//).",
            )
        else:
            return TechnicalCheckResult(
                check="SSL / HTTPS",
                status="pass",
                details="HTTPS is properly configured with no mixed content detected.",
            )
    except Exception as e:
        return TechnicalCheckResult(
            check="SSL / HTTPS",
            status="fail",
            details=f"SSL connection failed: {str(e)}",
            recommendation="Check your SSL certificate configuration. Use SSL Labs (ssllabs.com/ssltest) to diagnose issues.",
        )


async def check_redirects(url: str) -> TechnicalCheckResult:
    """Check for redirect chains and issues."""
    try:
        chain = []
        current_url = url

        async with httpx.AsyncClient(
            timeout=CHECK_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=False,
        ) as client:
            for _ in range(10):  # Max 10 hops to prevent infinite loops
                resp = await client.get(current_url)
                chain.append({"url": current_url, "status": resp.status_code})

                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get("location", "")
                    if not location:
                        break
                    # Handle relative redirects
                    if location.startswith("/"):
                        parsed = urlparse(current_url)
                        location = f"{parsed.scheme}://{parsed.netloc}{location}"
                    current_url = location
                else:
                    break

        if len(chain) == 1:
            return TechnicalCheckResult(
                check="Redirect Chain",
                status="pass",
                details="No redirects detected. URL resolves directly.",
            )
        elif len(chain) == 2:
            return TechnicalCheckResult(
                check="Redirect Chain",
                status="pass",
                details=f"Single redirect: {chain[0]['url']} ({chain[0]['status']}) → {chain[1]['url']}",
            )
        elif len(chain) <= 4:
            chain_str = " → ".join(f"{c['url']} ({c['status']})" for c in chain)
            return TechnicalCheckResult(
                check="Redirect Chain",
                status="warn",
                details=f"Redirect chain with {len(chain) - 1} hops: {chain_str}",
                recommendation="Reduce redirect chains to a single hop. Each redirect adds latency and dilutes link equity.",
            )
        else:
            return TechnicalCheckResult(
                check="Redirect Chain",
                status="fail",
                details=f"Long redirect chain with {len(chain) - 1} hops detected. This may indicate a redirect loop.",
                recommendation="Fix redirect chains immediately. Long chains severely impact page speed and may prevent search engines from crawling the page.",
            )
    except Exception as e:
        return TechnicalCheckResult(
            check="Redirect Chain",
            status="warn",
            details=f"Could not check redirects: {str(e)}",
        )


async def check_page_basics(client: httpx.AsyncClient, url: str) -> TechnicalCheckResult:
    """Check basic on-page technical elements: canonical, viewport, lang, charset."""
    try:
        resp = await client.get(url)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        issues = []

        # Canonical tag
        canonical = soup.find("link", rel="canonical")
        if not canonical:
            issues.append("Missing canonical tag")
        elif canonical.get("href") and canonical["href"] != url:
            canonical_url = canonical["href"]
            # Check if it's just a trailing slash difference
            if canonical_url.rstrip("/") != url.rstrip("/"):
                issues.append(f"Canonical URL ({canonical_url}) differs from page URL ({url})")

        # Viewport meta
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            issues.append("Missing viewport meta tag (hurts mobile SEO)")

        # Language attribute
        html_tag = soup.find("html")
        if html_tag and not html_tag.get("lang"):
            issues.append("Missing lang attribute on <html> tag")

        # Charset
        charset = soup.find("meta", attrs={"charset": True})
        charset_equiv = soup.find("meta", attrs={"http-equiv": "Content-Type"})
        if not charset and not charset_equiv:
            issues.append("Missing charset declaration")

        if not issues:
            return TechnicalCheckResult(
                check="Page Technical Elements",
                status="pass",
                details="Canonical tag, viewport meta, lang attribute, and charset are all properly set.",
            )
        elif len(issues) <= 2:
            return TechnicalCheckResult(
                check="Page Technical Elements",
                status="warn",
                details=f"Minor issues found: {'; '.join(issues)}",
                recommendation="Fix these technical elements to improve search engine compatibility and mobile friendliness.",
            )
        else:
            return TechnicalCheckResult(
                check="Page Technical Elements",
                status="fail",
                details=f"Multiple technical issues: {'; '.join(issues)}",
                recommendation="Address all technical issues. These are foundational elements that search engines expect on every page.",
            )
    except Exception as e:
        return TechnicalCheckResult(
            check="Page Technical Elements",
            status="fail",
            details=f"Could not analyze page: {str(e)}",
        )


# ─── Formatter ──────────────────────────────────────────────────────────────


def format_technical_audit(result: TechnicalAuditResult) -> str:
    """Format a TechnicalAuditResult into a readable string for Claude."""
    if result.error:
        return f"❌ Technical SEO audit error for {result.url}: {result.error}"

    status_icon = {
        "Healthy": "🟢",
        "Needs Attention": "🟡",
        "Critical": "🔴",
    }
    icon = status_icon.get(result.overall_status, "⚪")

    lines = [
        f"# Technical SEO Audit: {result.url}",
        f"## Overall Status: {icon} {result.overall_status}",
        f"*{result.passed} passed · {result.warnings} warnings · {result.failed} failed*",
        "",
        "---",
        "",
    ]

    check_icons = {"pass": "✅", "warn": "⚠️", "fail": "❌"}

    for check in result.checks:
        ci = check_icons.get(check.status, "⚪")
        lines.append(f"### {ci} {check.check}")
        lines.append(f"**Status**: {check.status.upper()}")
        if check.details:
            lines.append(f"**Details**: {check.details}")
        if check.recommendation:
            lines.append(f"**Recommendation**: {check.recommendation}")
        lines.append("")

    return "\n".join(lines)
