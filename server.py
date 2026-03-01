"""SEO Intelligence — MCP Server Entry Point.

Provides 12 SEO analysis tools to Claude via the Model Context Protocol.
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
    classify_search_intent,
    format_search_intent,
)
from technical import audit_technical_seo, format_technical_audit
from content import (
    generate_content_brief,
    cluster_keywords,
    detect_cannibalization,
    format_content_brief,
    format_keyword_clusters,
    format_cannibalization_report,
)
from ai_search import analyze_aeo_visibility, format_aeo_report
from entity import verify_entity, format_entity_report
from predictive import calculate_keyword_difficulty, format_predictive_report
from local_seo import (
    analyze_local_rankings, 
    generate_geo_tags, 
    generate_citation_list,
    format_local_seo_report,
    format_geo_tags,
    format_citations
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
        "PERPLEXITY_API_KEY": {
            "description": "Perplexity — AI Citation & AEO Visibility tracking",
            "required": False,
            "signup_url": "https://www.perplexity.ai/settings/api",
            "free_tier": "Paid API ($5 min deposit)",
        },
        "OPENAI_API_KEY": {
            "description": "OpenAI — ChatGPT AEO evaluation",
            "required": False,
            "signup_url": "https://platform.openai.com/",
            "free_tier": "Paid API",
        },
        "GOOGLE_CLOUD_API_KEY": {
            "description": "Google Cloud — Knowledge Graph Entity Verification",
            "required": False,
            "signup_url": "https://console.cloud.google.com/",
            "free_tier": "Free tier covers most usage",
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
            '        "SERPAPI_KEY": "your_serpapi_key_here",',
            '        "PERPLEXITY_API_KEY": "your_optional_perplexity_key",',
            '        "OPENAI_API_KEY": "your_optional_openai_key",',
            '        "GOOGLE_CLOUD_API_KEY": "your_optional_google_key"',
            '      }',
            '    }',
            '  }',
            '}',
            "```",
        ])

    return "\n".join(lines)


# ─── Tool 8: technical_seo_audit ─────────────────────────────────────────────


@mcp.tool()
async def technical_seo_audit(url: str) -> str:
    """Run a technical SEO audit on a URL.

    Checks infrastructure-level SEO elements:
    - Sitemap.xml presence and validity
    - Robots.txt configuration
    - SSL/HTTPS status and mixed content
    - Redirect chains and loops
    - Canonical tags, viewport meta, lang attribute, charset

    Reports each check as PASS/WARN/FAIL with actionable recommendations.

    Args:
        url: The URL to audit (e.g., "https://example.com")

    Returns:
        Technical SEO audit report with pass/warn/fail for each check.
    """
    try:
        result = await audit_technical_seo(url)
        return format_technical_audit(result)
    except Exception as e:
        return f"❌ Technical audit failed for {url}: {str(e)}"


# ─── Tool 9: classify_intent ─────────────────────────────────────────────────


@mcp.tool()
async def classify_intent(keyword: str) -> str:
    """Classify the search intent of a keyword.

    Searches Google for the keyword and analyzes SERP signals to determine
    whether the search intent is:
    - Informational (how-to, guides, definitions)
    - Navigational (looking for a specific site/brand)
    - Transactional (ready to buy/download/sign up)
    - Commercial (comparing options, reading reviews)

    Also recommends the best content type to create for the keyword.

    Args:
        keyword: The keyword to classify (e.g., "best coffee maker 2026")

    Returns:
        Intent classification with confidence score, reasoning, and content recommendation.
    """
    try:
        serp_response = await search_keyword(keyword, num_results=5)
        result = classify_search_intent(keyword, serp_response)
        return format_search_intent(result)
    except Exception as e:
        return f"❌ Intent classification failed for '{keyword}': {str(e)}"


# ─── Tool 10: content_brief ──────────────────────────────────────────────────


@mcp.tool()
async def content_brief(keyword: str) -> str:
    """Generate an SEO content brief for a keyword.

    Searches the keyword, analyzes top-ranking competitors, and generates
    a detailed content brief including:
    - Suggested title
    - Target word count (based on competitor average)
    - Recommended H2/H3 headings
    - Questions to answer (from People Also Ask + competitor FAQs)
    - Key topics to cover
    - Search intent classification

    Perfect for writers and content strategists planning new content.

    Args:
        keyword: The target keyword to create content for (e.g., "how to make cold brew coffee")

    Returns:
        A complete content brief with title, headings, word count target, and questions.
    """
    try:
        # Search SERP
        serp_response = await search_keyword(keyword, num_results=3)
        if serp_response.error:
            return f"❌ SERP search failed: {serp_response.error}"

        # Classify intent
        intent_result = classify_search_intent(keyword, serp_response)

        # Crawl top competitors
        competitor_pages: list[PageAnalysis] = []
        for result in serp_response.organic_results:
            try:
                comp_html = await crawl_page(result.url)
                comp_analysis = parse_page(comp_html, result.url)
                competitor_pages.append(comp_analysis)
            except Exception:
                continue

        if not competitor_pages:
            return "⚠️ Could not crawl any competitor pages for brief generation."

        # Generate brief
        brief = generate_content_brief(
            keyword, serp_response, competitor_pages, intent_result.intent
        )

        # Combine intent + brief
        intent_report = format_search_intent(intent_result)
        brief_report = format_content_brief(brief)

        return f"{intent_report}\n\n---\n\n{brief_report}"

    except Exception as e:
        return f"❌ Content brief generation failed for '{keyword}': {str(e)}"


# ─── Tool 11: keyword_cluster ────────────────────────────────────────────────


@mcp.tool()
async def keyword_cluster(keywords: list[str]) -> str:
    """Group related keywords into clusters based on SERP overlap.

    Keywords that share the same top-ranking URLs in Google likely target
    the same search intent and can be covered by a single page.

    This helps avoid creating multiple pages for the same intent
    (keyword cannibalization) and identifies opportunities for
    pillar/cluster content strategies.

    Args:
        keywords: List of keywords to cluster (e.g., ["cold brew coffee", "iced coffee", "cold brew recipe"])

    Returns:
        Keyword clusters with primary keywords and recommended page types.
    """
    try:
        if len(keywords) < 2:
            return "⚠️ Please provide at least 2 keywords to cluster."

        # Search SERP for each keyword
        serp_responses = []
        for kw in keywords:
            resp = await search_keyword(kw, num_results=5)
            serp_responses.append(resp)

        clusters = cluster_keywords(keywords, serp_responses)
        return format_keyword_clusters(clusters)

    except Exception as e:
        return f"❌ Keyword clustering failed: {str(e)}"


# ─── Tool 12: detect_keyword_cannibalization ─────────────────────────────────


@mcp.tool()
async def detect_keyword_cannibalization(domain: str, keywords: list[str]) -> str:
    """Detect keyword cannibalization for a domain.

    Checks if multiple pages from your domain are competing against each
    other in Google for the same keywords. When two of your pages rank
    for the same keyword, they split ranking signals and both perform worse.

    Args:
        domain: Your domain (e.g., "example.com")
        keywords: Keywords to check for cannibalization (e.g., ["coffee maker", "best coffee maker"])

    Returns:
        Cannibalization report with conflicting URLs and recommendations.
    """
    try:
        if not keywords:
            return "⚠️ Please provide at least 1 keyword to check."

        # Search SERP for each keyword
        serp_responses = []
        for kw in keywords:
            resp = await search_keyword(kw, num_results=10)
            serp_responses.append(resp)

        issues = detect_cannibalization(domain, keywords, serp_responses)
        return format_cannibalization_report(issues)

    except Exception as e:
        return f"❌ Cannibalization detection failed: {str(e)}"


# ─── Tool 13: check_aeo_visibility ───────────────────────────────────────────


@mcp.tool()
async def check_aeo_visibility(domain: str, keyword: str) -> str:
    """Check AI Search Engine citation status (AEO) for a domain.

    Queries AI search engines (Perplexity, OpenAI, Google SGE) to see
    if the specified domain is cited as a source for the keyword.
    
    This helps measure Answer Engine Optimization (AEO) performance.

    Args:
        domain: Your domain to check (e.g., "example.com")
        keyword: The target keyword or question

    Returns:
        A report showing visibility across available AI engines.
    """
    try:
        results = await analyze_aeo_visibility(domain, keyword)
        return format_aeo_report(domain, keyword, results)
    except Exception as e:
        return f"❌ AEO check failed: {str(e)}"


# ─── Tool 14: analyze_entity ─────────────────────────────────────────────────


@mcp.tool()
async def analyze_entity(keyword: str) -> str:
    """Verify an entity in the Google Knowledge Graph.

    Searches the official Google Knowledge Graph for a keyword or entity name.
    Returns the Knowledge Graph MID (Machine Readable Entity ID), description,
    and associated Wikipedia URL if found.
    
    This is critical for Entity SEO — mapping content to recognized
    concepts using schema markup properly.

    Args:
        keyword: The entity name or concept to search (e.g., "Starbucks")

    Returns:
        Structured Knowledge Graph information and schema recommendations.
    """
    try:
        results = await verify_entity(keyword)
        return format_entity_report(keyword, results)
    except Exception as e:
        return f"❌ Entity analysis failed: {str(e)}"


# ─── Tool 15: predict_keyword_difficulty ─────────────────────────────────────


@mcp.tool()
async def predict_keyword_difficulty(keyword: str) -> str:
    """Predict SEO ranking difficulty and traffic potential for a keyword.

    Analyzes the top 10 search results to estimate how hard it will be
    to rank (0-100 score). Looks at competitor title optimization and
    domain authority markers. Provides an ROI projection and timeline.

    Args:
        keyword: The target keyword to analyze

    Returns:
        Difficulty score, heuristics, and estimated ranking timeline.
    """
    try:
        serp_response = await search_keyword(keyword, num_results=10)
        score = await calculate_keyword_difficulty(keyword, serp_response)
        return format_predictive_report(score)
    except Exception as e:
        return f"❌ Predictive analysis failed: {str(e)}"


# ─── Tool 16: analyze_local_seo ──────────────────────────────────────────────


@mcp.tool()
async def analyze_local_seo(business_name: str, keywords: list[str], location: str) -> str:
    """Analyze a business's local search presence in the Google Local 3-Pack.

    Takes a business name, a target location, and keywords to query 
    Google. It checks if the business appears in the map pack (Local 3-Pack),
    extracting its rank, rating, and review counts.

    Args:
        business_name: The name of the business (e.g., "Starbucks")
        keywords: A list of target keywords (e.g., ["coffee shop", "cafe"])
        location: Target geographic location (e.g., "Seattle, WA", "10001, US")

    Returns:
        A report with Local Pack rankings and recommendations.
    """
    try:
        report = await analyze_local_rankings(business_name, keywords, location)
        return format_local_seo_report(report)
    except Exception as e:
        return f"❌ Local SEO analysis failed: {str(e)}"


# ─── Tool 17: generate_local_geo_tags ────────────────────────────────────────


@mcp.tool()
def generate_local_geo_tags(latitude: str, longitude: str, region: str, placename: str) -> str:
    """Generate geographical meta tags (geo tags) for a local business website.

    Local search relies on explicit location markers. These HTML <meta> tags 
    should be injected into the <head> of the website to help search engines 
    understand the exact physical location of the business.

    Args:
        latitude: The latitude of the business (e.g., "30.2672")
        longitude: The longitude of the business (e.g., "-97.7431")
        region: The standard ISO-3166 region code (e.g., "US-TX")
        placename: The city/town name (e.g., "Austin")

    Returns:
        Formatted HTML meta tags ready to be copy-pasted.
    """
    geo = generate_geo_tags(latitude, longitude, region, placename)
    return format_geo_tags(geo)


# ─── Tool 18: generate_citation_opportunities ────────────────────────────────


@mcp.tool()
def generate_citation_opportunities(business_category: str, name: str, address: str, phone: str) -> str:
    """Generate a prioritized list of local directories for citation building.

    Local SEO requires consistent NAP (Name, Address, Phone) data across 
    reputable directories. This tool automatically curates a high-authority 
    list of directories relevant to the business category to build citations on.

    Args:
        business_category: The industry category (e.g., "Restaurant", "Dentist", "Law Firm")
        name: The exact business name
        address: The exact business address
        phone: The exact business phone number

    Returns:
        A prioritized citation building plan and exact NAP block.
    """
    citations = generate_citation_list(business_category, name, address, phone)
    return format_citations(citations)


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
