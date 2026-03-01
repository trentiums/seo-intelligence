"""Content strategy module.

Provides content brief generation, keyword clustering (by SERP overlap),
and keyword cannibalization detection.
"""

from collections import Counter, defaultdict
from urllib.parse import urlparse

from models import (
    PageAnalysis,
    SerpResponse,
    ContentBrief,
    KeywordCluster,
    CannibalizationIssue,
)


# ─── Content Brief Generation ───────────────────────────────────────────────


def generate_content_brief(
    keyword: str,
    serp_response: SerpResponse,
    competitor_pages: list[PageAnalysis],
    search_intent: str = "",
) -> ContentBrief:
    """Generate a content brief based on competitor analysis.

    Analyzes top-ranking pages to extract common headings, average word count,
    questions to answer, and key topics for a target keyword.

    Args:
        keyword: The target keyword.
        serp_response: SERP data for the keyword.
        competitor_pages: Analyzed competitor pages.
        search_intent: Optional pre-classified search intent.

    Returns:
        A ContentBrief with recommended title, headings, word count, etc.
    """
    if not competitor_pages:
        return ContentBrief(
            keyword=keyword,
            error="No competitor pages available for analysis.",
        )

    brief = ContentBrief(keyword=keyword, search_intent=search_intent)

    # Competitor URLs
    brief.competitor_urls = [p.url for p in competitor_pages]

    # --- Word count target ---
    word_counts = [p.word_count for p in competitor_pages if p.word_count > 0]
    if word_counts:
        avg_wc = sum(word_counts) // len(word_counts)
        brief.competitor_avg_word_count = avg_wc
        # Target 10-20% more than competitor average
        brief.target_word_count = int(avg_wc * 1.15)

    # --- Suggested title ---
    brief.suggested_title = _suggest_title(keyword, competitor_pages)

    # --- Extract common headings from competitors ---
    brief.suggested_headings = _extract_common_headings(competitor_pages)

    # --- Questions to answer ---
    questions = []
    # From People Also Ask
    if serp_response.people_also_ask:
        questions.extend(serp_response.people_also_ask)
    # From competitor FAQ sections
    for page in competitor_pages:
        for faq in page.faqs:
            if faq.question and faq.question not in questions:
                questions.append(faq.question)
    brief.questions_to_answer = questions[:10]  # Cap at 10

    # --- Key topics from competitor content ---
    brief.key_topics = _extract_key_topics(keyword, competitor_pages)

    return brief


def _suggest_title(keyword: str, pages: list[PageAnalysis]) -> str:
    """Suggest a title based on competitor patterns."""
    # Analyze competitor title patterns
    title_lengths = [len(p.title) for p in pages if p.title]
    avg_length = sum(title_lengths) // len(title_lengths) if title_lengths else 60

    # Common patterns in SEO titles
    year = "2026"
    patterns = [
        f"{keyword.title()} — Complete Guide ({year})",
        f"{keyword.title()}: Everything You Need to Know",
        f"The Ultimate Guide to {keyword.title()} ({year})",
    ]

    # Pick pattern closest to average competitor title length
    best = min(patterns, key=lambda p: abs(len(p) - avg_length))
    return best


def _extract_common_headings(pages: list[PageAnalysis]) -> list[str]:
    """Extract commonly used headings across competitor pages."""
    heading_counter = Counter()

    for page in pages:
        seen = set()
        for h in page.headings:
            if h.level in (2, 3) and h.text:
                # Normalize heading text
                normalized = h.text.strip().lower()
                if normalized not in seen:
                    heading_counter[h.text.strip()] += 1
                    seen.add(normalized)

    # Return headings that appear in 2+ competitor pages, or top 8
    common = [h for h, count in heading_counter.most_common(15) if count >= 2]
    if not common:
        common = [h for h, _ in heading_counter.most_common(8)]

    return common[:10]


def _extract_key_topics(keyword: str, pages: list[PageAnalysis]) -> list[str]:
    """Extract key topics/themes from competitor content."""
    # Collect all headings as topic indicators
    topics = []
    seen = set()

    for page in pages:
        for h in page.headings:
            if h.level in (2, 3) and h.text:
                topic = h.text.strip()
                normalized = topic.lower()
                # Skip if it's just the keyword itself or too short
                if normalized not in seen and len(topic) > 5 and normalized != keyword.lower():
                    topics.append(topic)
                    seen.add(normalized)

    return topics[:12]


# ─── Keyword Clustering ─────────────────────────────────────────────────────


def cluster_keywords(
    keywords: list[str],
    serp_responses: list[SerpResponse],
) -> list[KeywordCluster]:
    """Group keywords by SERP URL overlap.

    Keywords that share ranking URLs likely target the same search intent
    and can be covered by a single page.

    Args:
        keywords: List of keywords to cluster.
        serp_responses: SERP responses for each keyword (same order).

    Returns:
        List of KeywordClusters with primary and related keywords.
    """
    if len(keywords) != len(serp_responses):
        return []

    # Build keyword → ranking URLs mapping
    keyword_urls: dict[str, set[str]] = {}
    for kw, resp in zip(keywords, serp_responses):
        if not resp.error:
            urls = {r.url for r in resp.organic_results}
            keyword_urls[kw] = urls
        else:
            keyword_urls[kw] = set()

    # Build overlap matrix
    clustered: set[str] = set()
    clusters: list[KeywordCluster] = []

    # Sort keywords by total results (descending) to pick broader terms as primaries
    sorted_kws = sorted(
        keywords,
        key=lambda k: next(
            (r.total_results for r in serp_responses if r.keyword == k), 0
        ),
        reverse=True,
    )

    for primary in sorted_kws:
        if primary in clustered:
            continue

        primary_urls = keyword_urls.get(primary, set())
        if not primary_urls:
            # No SERP data — standalone cluster
            clusters.append(KeywordCluster(
                cluster_name=primary.title(),
                primary_keyword=primary,
            ))
            clustered.add(primary)
            continue

        related = []
        shared = set()

        for other in sorted_kws:
            if other == primary or other in clustered:
                continue
            other_urls = keyword_urls.get(other, set())
            overlap = primary_urls & other_urls

            # Require at least 2 shared URLs for clustering
            if len(overlap) >= 2:
                related.append(other)
                shared.update(overlap)
                clustered.add(other)

        cluster = KeywordCluster(
            cluster_name=primary.title(),
            primary_keyword=primary,
            related_keywords=related,
            shared_urls=list(shared)[:5],
        )

        # Recommend page type based on cluster size
        if len(related) >= 4:
            cluster.recommended_page_type = "Pillar page (comprehensive, long-form)"
        elif len(related) >= 1:
            cluster.recommended_page_type = "In-depth blog post or guide"
        else:
            cluster.recommended_page_type = "Focused article or landing page"

        clusters.append(cluster)
        clustered.add(primary)

    return clusters


# ─── Keyword Cannibalization Detection ──────────────────────────────────────


def detect_cannibalization(
    domain: str,
    keywords: list[str],
    serp_responses: list[SerpResponse],
) -> list[CannibalizationIssue]:
    """Detect keyword cannibalization for a domain.

    Finds keywords where multiple pages from the same domain rank
    in the SERPs, indicating they're competing against each other.

    Args:
        domain: The domain to check (e.g., "example.com").
        keywords: List of keywords to check.
        serp_responses: SERP responses for each keyword (same order).

    Returns:
        List of CannibalizationIssues found.
    """
    # Normalize domain
    domain = domain.lower().replace("https://", "").replace("http://", "").rstrip("/")
    if domain.startswith("www."):
        domain_variants = [domain, domain[4:]]
    else:
        domain_variants = [domain, f"www.{domain}"]

    issues = []

    for kw, resp in zip(keywords, serp_responses):
        if resp.error:
            continue

        # Find all URLs from the target domain in organic results
        domain_urls = []
        for result in resp.organic_results:
            result_domain = urlparse(result.url).netloc.lower()
            if any(result_domain == d or result_domain.endswith(f".{d}") for d in domain_variants):
                domain_urls.append(result.url)

        if len(domain_urls) >= 2:
            # Cannibalization detected
            severity = "high" if len(domain_urls) >= 3 else "medium"
            issues.append(CannibalizationIssue(
                keyword=kw,
                conflicting_urls=domain_urls,
                severity=severity,
                recommendation=_cannibalization_recommendation(kw, domain_urls),
            ))

    return issues


def _cannibalization_recommendation(keyword: str, urls: list[str]) -> str:
    """Generate a recommendation for a cannibalization issue."""
    if len(urls) == 2:
        return (
            f"Two pages compete for '{keyword}'. Consider: "
            f"(1) Merge the content into one comprehensive page, "
            f"(2) Differentiate each page to target distinct intents, or "
            f"(3) Add a canonical tag from the weaker page to the stronger one."
        )
    else:
        return (
            f"{len(urls)} pages compete for '{keyword}'. This significantly dilutes ranking power. "
            f"Consolidate content into one authoritative page and redirect the others with 301 redirects."
        )


# ─── Formatters ──────────────────────────────────────────────────────────────


def format_content_brief(brief: ContentBrief) -> str:
    """Format a ContentBrief into a readable string for Claude."""
    if brief.error:
        return f"❌ Content brief error for '{brief.keyword}': {brief.error}"

    lines = [
        f"# Content Brief: \"{brief.keyword}\"",
        "",
    ]

    if brief.search_intent:
        lines.append(f"**Search Intent**: {brief.search_intent}")
        lines.append("")

    lines.extend([
        f"## Recommended Title",
        f"**{brief.suggested_title}**",
        "",
        f"## Target Word Count",
        f"**{brief.target_word_count:,} words** (competitor average: {brief.competitor_avg_word_count:,})",
        "",
    ])

    if brief.suggested_headings:
        lines.append("## Suggested Headings (H2/H3)")
        for h in brief.suggested_headings:
            lines.append(f"- {h}")
        lines.append("")

    if brief.questions_to_answer:
        lines.append("## Questions to Answer")
        for q in brief.questions_to_answer:
            lines.append(f"- {q}")
        lines.append("")

    if brief.key_topics:
        lines.append("## Key Topics to Cover")
        for t in brief.key_topics:
            lines.append(f"- {t}")
        lines.append("")

    if brief.competitor_urls:
        lines.append("## Competitor References")
        for i, url in enumerate(brief.competitor_urls, 1):
            lines.append(f"{i}. {url}")
        lines.append("")

    return "\n".join(lines)


def format_keyword_clusters(clusters: list[KeywordCluster]) -> str:
    """Format keyword clusters into a readable string for Claude."""
    if not clusters:
        return "No keyword clusters could be generated."

    lines = [
        f"# Keyword Clusters",
        f"*{len(clusters)} clusters identified*",
        "",
    ]

    for i, cluster in enumerate(clusters, 1):
        total_kws = 1 + len(cluster.related_keywords)
        lines.append(f"## Cluster {i}: {cluster.cluster_name} ({total_kws} keywords)")
        lines.append(f"**Primary keyword**: {cluster.primary_keyword}")

        if cluster.related_keywords:
            lines.append(f"**Related keywords**: {', '.join(cluster.related_keywords)}")

        if cluster.recommended_page_type:
            lines.append(f"**Recommended page type**: {cluster.recommended_page_type}")

        if cluster.shared_urls:
            lines.append(f"**Shared ranking URLs**: {len(cluster.shared_urls)}")

        lines.append("")

    return "\n".join(lines)


def format_cannibalization_report(issues: list[CannibalizationIssue]) -> str:
    """Format cannibalization issues into a readable string for Claude."""
    if not issues:
        return "✅ No keyword cannibalization issues detected. Each keyword maps to a single page."

    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}

    lines = [
        f"# Keyword Cannibalization Report",
        f"*{len(issues)} cannibalization issues found*",
        "",
    ]

    for issue in issues:
        icon = severity_icon.get(issue.severity, "⚪")
        lines.append(f"## {icon} \"{issue.keyword}\" — {issue.severity.upper()} severity")
        lines.append(f"**Conflicting pages** ({len(issue.conflicting_urls)}):")
        for url in issue.conflicting_urls:
            lines.append(f"- {url}")
        if issue.recommendation:
            lines.append(f"**Recommendation**: {issue.recommendation}")
        lines.append("")

    return "\n".join(lines)
