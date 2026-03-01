"""SEO Intelligence — MCP Server Entry Point.

Provides 7 SEO analysis tools to Claude via the Model Context Protocol.
Run with: uv run server.py
"""

import os
import asyncio

from mcp.server.fastmcp import FastMCP

from crawler import crawl_page, parse_page, format_page_analysis
from serp import search_keyword, format_serp_response
from analyzer import (
    calculate_seo_score,
    compare_pages,
    generate_action_plan,
    find_quick_wins,
    format_gap_report,
    format_ranking_plan,
    format_quick_wins,
    format_seo_score,
)
from models import PageAnalysis


# Initialize MCP server
mcp = FastMCP("seo-intelligence")


# ─── Tool 1: analyze_page ────────────────────────────────────────────────────


@mcp.tool()
async def analyze_page(url: str) -> str:
    """Analyze the SEO of a web page.

    Crawls the URL and provides a complete on-page SEO analysis including:
    title tag, meta description, heading hierarchy (H1-H6), word count,
    internal/external link counts, image alt text coverage, FAQ detection,
    schema markup presence, Open Graph tags, and an SEO score (0-100).

    Args:
        url: The full URL of the page to analyze (e.g., "https://example.com/page")

    Returns:
        A formatted SEO analysis report with actionable insights.
    """
    try:
        html = await crawl_page(url)
        analysis = parse_page(html, url)
        score = calculate_seo_score(analysis)

        report = format_page_analysis(analysis)
        score_report = format_seo_score(score, url)

        return f"{report}\n\n---\n\n{score_report}"
    except Exception as e:
        return f"❌ Failed to analyze {url}: {str(e)}"


# ─── Tool 2: search_serp ─────────────────────────────────────────────────────


@mcp.tool()
async def search_serp(keyword: str, num_results: int = 3) -> str:
    """Search Google for a keyword and return top organic results.

    Uses SerpAPI (requires SERPAPI_KEY environment variable) to fetch
    real-time SERP data including organic rankings, SERP features
    (featured snippets, PAA, knowledge panels, etc.), and People Also Ask.

    Args:
        keyword: The search query/keyword to look up
        num_results: Number of top organic results to return (default: 3, max: 10)

    Returns:
        SERP results with positions, titles, URLs, snippets, and SERP features.
    """
    num_results = min(max(num_results, 1), 10)
    response = await search_keyword(keyword, num_results=num_results)
    return format_serp_response(response)


# ─── Tool 3: compare_with_competitors ────────────────────────────────────────


@mcp.tool()
async def compare_with_competitors(user_url: str, keyword: str) -> str:
    """Compare your page against top-ranking competitors for a keyword.

    Searches the keyword on Google, identifies the top 3 ranking pages,
    crawls and analyzes each one, then performs a detailed gap analysis
    comparing your page against competitors across:
    - Content depth (word count)
    - Heading structure (H1-H6)
    - Meta tags (title, description)
    - FAQ sections
    - Schema markup
    - Link profile (internal/external)
    - Image optimization

    Args:
        user_url: Your page URL to compare
        keyword: The target keyword to search for competitors

    Returns:
        A gap analysis report showing where your page falls short vs. competitors.
    """
    try:
        # Step 1: Analyze user's page
        user_html = await crawl_page(user_url)
        user_analysis = parse_page(user_html, user_url)

        # Step 2: Search SERP for top competitors
        serp_response = await search_keyword(keyword, num_results=3)
        if serp_response.error:
            return f"❌ SERP search failed: {serp_response.error}"

        # Step 3: Analyze competitor pages (in parallel)
        competitor_analyses: list[PageAnalysis] = []
        for result in serp_response.organic_results:
            # Skip if competitor URL is same as user URL
            if result.url.rstrip("/") == user_url.rstrip("/"):
                continue
            try:
                comp_html = await crawl_page(result.url)
                comp_analysis = parse_page(comp_html, result.url)
                competitor_analyses.append(comp_analysis)
            except Exception:
                continue  # Skip unreachable competitors

        if not competitor_analyses:
            return "⚠️ Could not crawl any competitor pages. They may be blocking automated access."

        # Step 4: Compare
        gap_report = compare_pages(user_analysis, competitor_analyses)
        gap_report.keyword = keyword

        return format_gap_report(gap_report)

    except Exception as e:
        return f"❌ Comparison failed: {str(e)}"


# ─── Tool 4: generate_ranking_plan ───────────────────────────────────────────


@mcp.tool()
async def generate_ranking_plan(user_url: str, keyword: str) -> str:
    """Generate a prioritized action plan to rank higher for a keyword.

    Performs a competitor comparison, identifies gaps, and creates a
    numbered, prioritized list of specific SEO improvements with:
    - Exact on-page changes to make
    - Effort level (Easy/Medium/Hard)
    - Expected impact (High/Medium/Low)
    - Category (meta/content/structure/schema/technical)

    Args:
        user_url: Your page URL to improve
        keyword: The target keyword to rank for

    Returns:
        A prioritized ranking plan with specific action items.
    """
    try:
        # Step 1: Analyze user's page
        user_html = await crawl_page(user_url)
        user_analysis = parse_page(user_html, user_url)

        # Step 2: Search SERP
        serp_response = await search_keyword(keyword, num_results=3)
        if serp_response.error:
            # If no SERP data, generate plan from page analysis alone
            quick = find_quick_wins(user_analysis)
            return (
                f"⚠️ SERP data unavailable ({serp_response.error}). "
                f"Here's a plan based on page analysis alone:\n\n"
                f"{format_quick_wins(quick, user_url)}"
            )

        # Step 3: Analyze competitors
        competitor_analyses: list[PageAnalysis] = []
        for result in serp_response.organic_results:
            if result.url.rstrip("/") == user_url.rstrip("/"):
                continue
            try:
                comp_html = await crawl_page(result.url)
                comp_analysis = parse_page(comp_html, result.url)
                competitor_analyses.append(comp_analysis)
            except Exception:
                continue

        # Step 4: Compare and generate plan
        gap_report = compare_pages(user_analysis, competitor_analyses)
        gap_report.keyword = keyword
        plan = generate_action_plan(gap_report)

        # Include SERP context
        serp_context = format_serp_response(serp_response)

        return f"{serp_context}\n\n---\n\n{format_ranking_plan(plan)}"

    except Exception as e:
        return f"❌ Plan generation failed: {str(e)}"


# ─── Tool 5: quick_wins ──────────────────────────────────────────────────────


@mcp.tool()
async def quick_wins(url: str) -> str:
    """Find the 5 easiest SEO fixes with highest impact for a page.

    Analyzes the page and identifies the top 5 quick wins — changes that
    require minimal effort but have significant SEO impact. Great for
    getting started with SEO optimization.

    Examples of quick wins:
    - Adding a missing meta description
    - Fixing H1 tag problems
    - Adding FAQ schema markup
    - Adding alt text to images
    - Adding Open Graph tags

    Args:
        url: The page URL to analyze for quick wins

    Returns:
        Top 5 quick-win recommendations sorted by impact and ease.
    """
    try:
        html = await crawl_page(url)
        analysis = parse_page(html, url)

        # Calculate score first
        score = calculate_seo_score(analysis)
        wins = find_quick_wins(analysis)

        score_intro = f"**Current SEO Score: {score.overall}/100**\n\n"
        if not wins:
            return f"{score_intro}✅ Great job! No quick wins found — your page covers all the basics."

        return f"{score_intro}{format_quick_wins(wins, url)}"

    except Exception as e:
        return f"❌ Quick wins analysis failed for {url}: {str(e)}"


# ─── Tool 6: full_audit ──────────────────────────────────────────────────────


@mcp.tool()
async def full_audit(url: str, keywords: list[str]) -> str:
    """Run a complete SEO audit across multiple keywords.

    Performs a comprehensive audit that:
    1. Analyzes the page's SEO health (score 0-100)
    2. For each keyword, compares against top-ranking competitors
    3. Generates per-keyword ranking plans
    4. Aggregates findings into an overall report

    Best for getting a complete picture of where a page stands and
    what to fix to improve rankings across multiple target keywords.

    Args:
        url: The page URL to audit
        keywords: List of target keywords to analyze (e.g., ["best coffee maker", "coffee machine reviews"])

    Returns:
        Complete SEO audit with per-keyword plans and overall site score.
    """
    try:
        # Page analysis + score
        html = await crawl_page(url)
        page_analysis = parse_page(html, url)
        score = calculate_seo_score(page_analysis)

        report_parts = [
            f"# Full SEO Audit: {url}",
            f"## Overall SEO Score: {score.overall}/100",
            "",
            format_seo_score(score, url),
            "",
            "---",
            "",
        ]

        # Quick wins
        wins = find_quick_wins(page_analysis)
        if wins:
            report_parts.append(format_quick_wins(wins, url))
            report_parts.extend(["", "---", ""])

        # Per-keyword analysis
        report_parts.append(f"# Per-Keyword Analysis ({len(keywords)} keywords)")
        report_parts.append("")

        for i, keyword in enumerate(keywords, 1):
            report_parts.append(f"## Keyword {i}/{len(keywords)}: \"{keyword}\"")
            report_parts.append("")

            serp_response = await search_keyword(keyword, num_results=3)

            if serp_response.error:
                report_parts.append(f"⚠️ SERP data unavailable: {serp_response.error}")
                report_parts.extend(["", "---", ""])
                continue

            # Competitor analysis
            competitor_analyses: list[PageAnalysis] = []
            for result in serp_response.organic_results:
                if result.url.rstrip("/") == url.rstrip("/"):
                    continue
                try:
                    comp_html = await crawl_page(result.url)
                    comp_analysis = parse_page(comp_html, result.url)
                    competitor_analyses.append(comp_analysis)
                except Exception:
                    continue

            if competitor_analyses:
                gap_report = compare_pages(page_analysis, competitor_analyses)
                gap_report.keyword = keyword
                plan = generate_action_plan(gap_report)

                report_parts.append(format_gap_report(gap_report))
                report_parts.extend(["", "---", ""])
                report_parts.append(format_ranking_plan(plan))
            else:
                report_parts.append("⚠️ Could not crawl competitors for this keyword.")

            report_parts.extend(["", "---", ""])

        return "\n".join(report_parts)

    except Exception as e:
        return f"❌ Full audit failed for {url}: {str(e)}"


# ─── Tool 7: check_api_keys ──────────────────────────────────────────────────


@mcp.tool()
async def check_api_keys() -> str:
    """Check the status of required API keys for the SEO Intelligence plugin.

    Validates that all required environment variables are configured.
    Shows the status of each key and provides sign-up links for any
    missing keys.

    Returns:
        Status report of all API keys with setup instructions for missing ones.
    """
    keys = {
        "SERPAPI_KEY": {
            "description": "SerpAPI — SERP data and keyword rankings",
            "required": True,
            "signup_url": "https://serpapi.com/users/sign_up?source=seo-intelligence",
            "free_tier": "100 searches/month free",
        },
    }

    lines = [
        "# API Key Status — SEO Intelligence Plugin",
        "",
    ]

    all_set = True
    for key_name, info in keys.items():
        value = os.environ.get(key_name, "")
        is_set = bool(value)
        status = "✅ Configured" if is_set else "❌ Missing"
        required = "Required" if info["required"] else "Optional"

        if not is_set:
            all_set = False

        lines.extend([
            f"## {key_name}",
            f"- **Status**: {status}",
            f"- **Priority**: {required}",
            f"- **Purpose**: {info['description']}",
            f"- **Free tier**: {info['free_tier']}",
        ])

        if not is_set:
            lines.append(f"- **Sign up**: {info['signup_url']}")

        lines.append("")

    if all_set:
        lines.extend([
            "---",
            "✅ **All keys configured!** You're ready to use all SEO Intelligence tools.",
        ])
    else:
        lines.extend([
            "---",
            "## How to Configure Keys",
            "",
            "Add your keys to the `env` section of your Claude Desktop config:",
            "",
            "```json",
            '{',
            '  "mcpServers": {',
            '    "seo-intelligence": {',
            '      "command": "uv",',
            '      "args": ["--directory", "C:/path/to/seo-plugin", "run", "server.py"],',
            '      "env": {',
            '        "SERPAPI_KEY": "your_key_here"',
            '      }',
            '    }',
            '  }',
            '}',
            "```",
        ])

    return "\n".join(lines)


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
