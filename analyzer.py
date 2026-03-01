"""Gap analysis, SEO scoring, search intent classification, and ranking plan generation."""

import re

from models import (
    PageAnalysis,
    GapDimension,
    GapReport,
    ActionItem,
    RankingPlan,
    SeoScore,
    SerpResponse,
    SearchIntentResult,
)


# ─── SEO Scoring ─────────────────────────────────────────────────────────────


def calculate_seo_score(page: PageAnalysis) -> SeoScore:
    """Calculate a 0-100 SEO score for a page analysis.

    Scoring weights:
        - Title: 15 points
        - Meta description: 10 points
        - Headings: 15 points
        - Content depth: 20 points
        - Links: 10 points
        - Images: 10 points
        - Schema: 10 points
        - Technical: 10 points
    """
    score = SeoScore()

    # Title (15 pts)
    if page.title:
        title_len = len(page.title)
        if 30 <= title_len <= 60:
            score.title_score = 15
        elif 20 <= title_len <= 70:
            score.title_score = 10
        elif title_len > 0:
            score.title_score = 5
    score.breakdown["title"] = score.title_score

    # Meta description (10 pts)
    if page.meta_description:
        desc_len = len(page.meta_description)
        if 120 <= desc_len <= 160:
            score.meta_score = 10
        elif 80 <= desc_len <= 200:
            score.meta_score = 7
        elif desc_len > 0:
            score.meta_score = 3
    score.breakdown["meta_description"] = score.meta_score

    # Headings (15 pts)
    heading_score = 0
    if page.h1_count == 1:
        heading_score += 7  # Exactly 1 H1 is ideal
    elif page.h1_count > 1:
        heading_score += 3  # Multiple H1s is a problem
    if page.h2_count >= 2:
        heading_score += 5
    elif page.h2_count >= 1:
        heading_score += 3
    if page.h3_count >= 1:
        heading_score += 3
    score.headings_score = min(heading_score, 15)
    score.breakdown["headings"] = score.headings_score

    # Content depth (20 pts)
    if page.word_count >= 1500:
        score.content_score = 20
    elif page.word_count >= 800:
        score.content_score = 15
    elif page.word_count >= 300:
        score.content_score = 10
    elif page.word_count >= 100:
        score.content_score = 5
    else:
        score.content_score = 0
    score.breakdown["content"] = score.content_score

    # Links (10 pts)
    link_score = 0
    if page.internal_link_count >= 5:
        link_score += 5
    elif page.internal_link_count >= 2:
        link_score += 3
    if page.external_link_count >= 2:
        link_score += 5
    elif page.external_link_count >= 1:
        link_score += 3
    score.links_score = min(link_score, 10)
    score.breakdown["links"] = score.links_score

    # Images (10 pts)
    img_score = 0
    if page.total_images >= 1:
        img_score += 3  # Has images
        if page.image_alt_coverage == 100:
            img_score += 7
        elif page.image_alt_coverage >= 80:
            img_score += 5
        elif page.image_alt_coverage >= 50:
            img_score += 3
    else:
        img_score = 5  # No images isn't necessarily bad (depends on content type)
    score.images_score = min(img_score, 10)
    score.breakdown["images"] = score.images_score

    # Schema (10 pts)
    if page.has_schema:
        schema_count = len(page.schema_types)
        if schema_count >= 3:
            score.schema_score = 10
        elif schema_count >= 2:
            score.schema_score = 8
        else:
            score.schema_score = 5
    # Bonus for FAQ schema
    if page.has_faq_section:
        score.schema_score = min(score.schema_score + 2, 10)
    score.breakdown["schema"] = score.schema_score

    # Technical (10 pts)
    tech_score = 0
    if page.has_viewport_meta:
        tech_score += 3
    if page.has_lang_attribute:
        tech_score += 3
    if page.has_charset:
        tech_score += 2
    if page.canonical_url:
        tech_score += 2
    score.technical_score = min(tech_score, 10)
    score.breakdown["technical"] = score.technical_score

    # Overall
    score.overall = (
        score.title_score
        + score.meta_score
        + score.headings_score
        + score.content_score
        + score.links_score
        + score.images_score
        + score.schema_score
        + score.technical_score
    )

    return score


# ─── Gap Analysis ────────────────────────────────────────────────────────────


def compare_pages(
    user_page: PageAnalysis,
    competitor_pages: list[PageAnalysis],
) -> GapReport:
    """Compare user page against competitor pages and identify gaps.

    Args:
        user_page: The user's page analysis.
        competitor_pages: List of competitor page analyses.

    Returns:
        A GapReport with dimension-by-dimension comparison.
    """
    if not competitor_pages:
        return GapReport(
            user_url=user_page.url,
            keyword="",
            summary="No competitor pages to compare against.",
        )

    report = GapReport(
        user_url=user_page.url,
        keyword="",
        competitor_urls=[p.url for p in competitor_pages],
    )

    # Calculate avg competitor metrics
    avg_word_count = _avg([p.word_count for p in competitor_pages])
    avg_h2_count = _avg([p.h2_count for p in competitor_pages])
    avg_h3_count = _avg([p.h3_count for p in competitor_pages])
    avg_internal_links = _avg([p.internal_link_count for p in competitor_pages])
    avg_external_links = _avg([p.external_link_count for p in competitor_pages])
    avg_images = _avg([p.total_images for p in competitor_pages])
    competitors_with_faq = sum(1 for p in competitor_pages if p.has_faq_section)
    competitors_with_schema = sum(1 for p in competitor_pages if p.has_schema)

    # --- Word Count ---
    wc_gap = avg_word_count - user_page.word_count
    if wc_gap > 200:
        report.gaps.append(GapDimension(
            dimension="Content Depth (Word Count)",
            user_value=str(user_page.word_count),
            competitor_avg=str(int(avg_word_count)),
            gap=f"{int(wc_gap)} words behind",
            recommendation=f"Add approximately {int(wc_gap)} more words of relevant, high-quality content.",
            severity="high" if wc_gap > 500 else "medium",
        ))

    # --- Title ---
    if not user_page.title:
        report.gaps.append(GapDimension(
            dimension="Title Tag",
            user_value="MISSING",
            competitor_avg="Present",
            gap="No title tag",
            recommendation="Add a compelling, keyword-rich title tag (30-60 characters).",
            severity="high",
        ))
    elif len(user_page.title) < 30 or len(user_page.title) > 60:
        report.gaps.append(GapDimension(
            dimension="Title Tag Length",
            user_value=f"{len(user_page.title)} chars",
            competitor_avg="30-60 chars (recommended)",
            gap="Title length not optimal",
            recommendation="Adjust title to 30-60 characters with primary keyword near the beginning.",
            severity="medium",
        ))

    # --- Meta Description ---
    if not user_page.meta_description:
        report.gaps.append(GapDimension(
            dimension="Meta Description",
            user_value="MISSING",
            competitor_avg="Present",
            gap="No meta description",
            recommendation="Add a compelling meta description (120-160 characters) with target keyword and CTA.",
            severity="high",
        ))

    # --- H1 ---
    if user_page.h1_count != 1:
        report.gaps.append(GapDimension(
            dimension="H1 Tag",
            user_value=f"{user_page.h1_count} H1 tags",
            competitor_avg="1 H1 tag",
            gap="Incorrect H1 count",
            recommendation="Use exactly one H1 tag containing the primary keyword.",
            severity="high",
        ))

    # --- H2s ---
    h2_gap = avg_h2_count - user_page.h2_count
    if h2_gap > 1:
        report.gaps.append(GapDimension(
            dimension="H2 Subheadings",
            user_value=str(user_page.h2_count),
            competitor_avg=str(int(avg_h2_count)),
            gap=f"{int(h2_gap)} fewer H2s than competitors",
            recommendation=f"Add {int(h2_gap)} more H2 subheadings to improve content structure and keyword targeting.",
            severity="medium",
        ))

    # --- H3s ---
    h3_gap = avg_h3_count - user_page.h3_count
    if h3_gap > 1:
        report.gaps.append(GapDimension(
            dimension="H3 Subheadings",
            user_value=str(user_page.h3_count),
            competitor_avg=str(int(avg_h3_count)),
            gap=f"{int(h3_gap)} fewer H3s",
            recommendation="Add more H3 subheadings under H2s to create deeper content hierarchy.",
            severity="low",
        ))

    # --- Internal Links ---
    link_gap = avg_internal_links - user_page.internal_link_count
    if link_gap > 3:
        report.gaps.append(GapDimension(
            dimension="Internal Links",
            user_value=str(user_page.internal_link_count),
            competitor_avg=str(int(avg_internal_links)),
            gap=f"{int(link_gap)} fewer internal links",
            recommendation="Add more internal links to related pages to improve site structure and distribute authority.",
            severity="medium",
        ))

    # --- External Links ---
    ext_gap = avg_external_links - user_page.external_link_count
    if ext_gap > 1 and user_page.external_link_count == 0:
        report.gaps.append(GapDimension(
            dimension="External Links",
            user_value=str(user_page.external_link_count),
            competitor_avg=str(int(avg_external_links)),
            gap="No external links",
            recommendation="Add 2-3 external links to high-authority sources to signal content credibility.",
            severity="medium",
        ))

    # --- Images ---
    img_gap = avg_images - user_page.total_images
    if img_gap > 2:
        report.gaps.append(GapDimension(
            dimension="Images",
            user_value=str(user_page.total_images),
            competitor_avg=str(int(avg_images)),
            gap=f"{int(img_gap)} fewer images",
            recommendation="Add more relevant images with descriptive alt text to improve engagement.",
            severity="low",
        ))

    # --- Image Alt Text ---
    if user_page.total_images > 0 and user_page.image_alt_coverage < 100:
        report.gaps.append(GapDimension(
            dimension="Image Alt Text",
            user_value=f"{user_page.image_alt_coverage}% coverage",
            competitor_avg="100% recommended",
            gap=f"{user_page.images_without_alt} images missing alt text",
            recommendation="Add descriptive, keyword-relevant alt text to all images.",
            severity="medium",
        ))

    # --- FAQ ---
    if not user_page.has_faq_section and competitors_with_faq > 0:
        report.gaps.append(GapDimension(
            dimension="FAQ Section",
            user_value="Missing",
            competitor_avg=f"{competitors_with_faq}/{len(competitor_pages)} competitors have FAQs",
            gap="No FAQ section",
            recommendation="Add an FAQ section with structured data (FAQPage schema) targeting 'People Also Ask' queries.",
            severity="high",
        ))

    # --- Schema ---
    if not user_page.has_schema and competitors_with_schema > 0:
        report.gaps.append(GapDimension(
            dimension="Schema Markup",
            user_value="Missing",
            competitor_avg=f"{competitors_with_schema}/{len(competitor_pages)} competitors have schema",
            gap="No structured data",
            recommendation="Add JSON-LD schema markup (Article, FAQPage, BreadcrumbList) to improve rich snippet eligibility.",
            severity="high",
        ))

    # --- OG Tags ---
    if not user_page.has_og_tags:
        report.gaps.append(GapDimension(
            dimension="Open Graph Tags",
            user_value="Missing",
            competitor_avg="Present",
            gap="No OG tags",
            recommendation="Add Open Graph tags (og:title, og:description, og:image) for better social sharing.",
            severity="low",
        ))

    # Scores
    user_score = calculate_seo_score(user_page)
    comp_scores = [calculate_seo_score(p) for p in competitor_pages]
    report.user_score = user_score.overall
    report.competitor_avg_score = int(_avg([s.overall for s in comp_scores]))

    # Summary
    gap_count = len(report.gaps)
    high_severity = sum(1 for g in report.gaps if g.severity == "high")
    report.summary = (
        f"Found {gap_count} gaps between your page and top competitors. "
        f"{high_severity} are high severity. "
        f"Your SEO score: {report.user_score}/100 vs. competitor avg: {report.competitor_avg_score}/100."
    )

    return report


# ─── Action Plan Generation ──────────────────────────────────────────────────


def generate_action_plan(gap_report: GapReport) -> RankingPlan:
    """Generate a prioritized ranking plan from a gap report.

    Args:
        gap_report: The gap analysis report.

    Returns:
        A RankingPlan with numbered, prioritized action items.
    """
    plan = RankingPlan(
        url=gap_report.user_url,
        keyword=gap_report.keyword,
    )

    # Map gaps to action items with priority scoring
    actions: list[ActionItem] = []

    for gap in gap_report.gaps:
        effort, impact = _classify_gap(gap)
        category = _categorize_gap(gap.dimension)

        actions.append(ActionItem(
            priority=0,  # Will be set below
            description=gap.recommendation,
            category=category,
            effort=effort,
            impact=impact,
            details=f"Current: {gap.user_value} | Competitors: {gap.competitor_avg} | Gap: {gap.gap}",
        ))

    # Sort by impact (High first), then effort (Easy first)
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    effort_order = {"Easy": 0, "Medium": 1, "Hard": 2}
    actions.sort(key=lambda a: (impact_order.get(a.impact, 1), effort_order.get(a.effort, 1)))

    # Assign priority numbers
    for i, action in enumerate(actions, 1):
        action.priority = i

    plan.action_items = actions
    plan.current_issues = [g.gap for g in gap_report.gaps]

    # Estimate score improvement
    score_gap = gap_report.competitor_avg_score - gap_report.user_score
    estimated_improvement = int(score_gap * 0.7)  # Conservative estimate
    plan.estimated_score_after = min(gap_report.user_score + estimated_improvement, 100)

    plan.summary = (
        f"Identified {len(actions)} action items for '{gap_report.keyword}'. "
        f"Fixing all issues could improve your score from {gap_report.user_score} "
        f"to ~{plan.estimated_score_after}/100."
    )

    return plan


def find_quick_wins(page: PageAnalysis) -> list[ActionItem]:
    """Find the top 5 easiest, highest-impact fixes for a page.

    Args:
        page: The page analysis.

    Returns:
        Up to 5 ActionItems sorted by ease + impact.
    """
    wins: list[ActionItem] = []

    # Missing title
    if not page.title:
        wins.append(ActionItem(
            priority=0,
            description="Add a title tag",
            category="meta",
            effort="Easy",
            impact="High",
            details="Title tags are the #1 on-page ranking factor. Add a keyword-rich title (30-60 chars).",
        ))
    elif len(page.title) < 30 or len(page.title) > 60:
        wins.append(ActionItem(
            priority=0,
            description=f"Optimize title length (currently {len(page.title)} chars → aim for 30-60)",
            category="meta",
            effort="Easy",
            impact="Medium",
            details="Adjust title tag length for optimal display in search results.",
        ))

    # Missing meta description
    if not page.meta_description:
        wins.append(ActionItem(
            priority=0,
            description="Add a meta description",
            category="meta",
            effort="Easy",
            impact="High",
            details="Meta descriptions improve click-through rate from search results. 120-160 characters recommended.",
        ))

    # Missing or multiple H1
    if page.h1_count == 0:
        wins.append(ActionItem(
            priority=0,
            description="Add an H1 heading",
            category="structure",
            effort="Easy",
            impact="High",
            details="Every page needs exactly one H1 containing the primary keyword.",
        ))
    elif page.h1_count > 1:
        wins.append(ActionItem(
            priority=0,
            description=f"Reduce H1 tags from {page.h1_count} to 1",
            category="structure",
            effort="Easy",
            impact="Medium",
            details="Multiple H1 tags dilute relevance. Keep one primary H1.",
        ))

    # No FAQ section
    if not page.has_faq_section:
        wins.append(ActionItem(
            priority=0,
            description="Add an FAQ section with FAQPage schema",
            category="schema",
            effort="Medium",
            impact="High",
            details="FAQ sections with schema markup can trigger rich results and capture PAA traffic.",
        ))

    # No schema markup
    if not page.has_schema and page.has_faq_section:
        wins.append(ActionItem(
            priority=0,
            description="Add structured data markup (JSON-LD)",
            category="schema",
            effort="Medium",
            impact="High",
            details="Schema markup improves search engine understanding and enables rich snippets.",
        ))

    # Images missing alt text
    if page.images_without_alt > 0:
        wins.append(ActionItem(
            priority=0,
            description=f"Add alt text to {page.images_without_alt} images",
            category="content",
            effort="Easy",
            impact="Medium",
            details="Alt text improves accessibility and image search ranking.",
        ))

    # Thin content
    if page.word_count < 300:
        wins.append(ActionItem(
            priority=0,
            description=f"Expand content (currently {page.word_count} words → aim for 800+)",
            category="content",
            effort="Hard",
            impact="High",
            details="Thin content rarely ranks. Add comprehensive, valuable content covering the topic in depth.",
        ))

    # No OG tags
    if not page.has_og_tags:
        wins.append(ActionItem(
            priority=0,
            description="Add Open Graph meta tags",
            category="meta",
            effort="Easy",
            impact="Low",
            details="OG tags improve how your page appears when shared on social media.",
        ))

    # Missing viewport meta
    if not page.has_viewport_meta:
        wins.append(ActionItem(
            priority=0,
            description="Add viewport meta tag for mobile responsiveness",
            category="technical",
            effort="Easy",
            impact="Medium",
            details="Google uses mobile-first indexing. A viewport meta tag is essential.",
        ))

    # No canonical
    if not page.canonical_url:
        wins.append(ActionItem(
            priority=0,
            description="Add a canonical URL tag",
            category="technical",
            effort="Easy",
            impact="Medium",
            details="Canonical tags prevent duplicate content issues and consolidate ranking signals.",
        ))

    # Sort: High impact + Easy effort first
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    effort_order = {"Easy": 0, "Medium": 1, "Hard": 2}
    wins.sort(key=lambda a: (impact_order.get(a.impact, 1), effort_order.get(a.effort, 1)))

    # Top 5
    top_wins = wins[:5]
    for i, w in enumerate(top_wins, 1):
        w.priority = i

    return top_wins


# ─── Formatters ──────────────────────────────────────────────────────────────


def format_gap_report(report: GapReport) -> str:
    """Format a GapReport into a readable string."""
    lines = [
        f"# Gap Analysis: {report.user_url}",
        f"**Keyword**: {report.keyword}",
        f"**Your SEO Score**: {report.user_score}/100",
        f"**Competitor Avg Score**: {report.competitor_avg_score}/100",
        "",
        f"**Summary**: {report.summary}",
        "",
    ]

    if report.competitor_urls:
        lines.append("## Competitors Analyzed")
        for i, url in enumerate(report.competitor_urls, 1):
            lines.append(f"{i}. {url}")
        lines.append("")

    if report.gaps:
        lines.append("## Gaps Found")
        lines.append("")
        for gap in report.gaps:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(gap.severity, "⚪")
            lines.extend([
                f"### {severity_icon} {gap.dimension}",
                f"- **Your page**: {gap.user_value}",
                f"- **Competitor avg**: {gap.competitor_avg}",
                f"- **Gap**: {gap.gap}",
                f"- **Fix**: {gap.recommendation}",
                "",
            ])
    else:
        lines.append("✅ No significant gaps found! Your page is competitive.")

    return "\n".join(lines)


def format_ranking_plan(plan: RankingPlan) -> str:
    """Format a RankingPlan into a readable string."""
    lines = [
        f"# Ranking Plan: {plan.url}",
        f"**Target Keyword**: {plan.keyword}",
        f"**Summary**: {plan.summary}",
        "",
        "## Action Items (Priority Order)",
        "",
    ]

    for item in plan.action_items:
        effort_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(item.effort, "⚪")
        impact_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(item.impact, "⚪")
        lines.extend([
            f"### #{item.priority}: {item.description}",
            f"- **Category**: {item.category}",
            f"- **Effort**: {effort_icon} {item.effort}",
            f"- **Impact**: {impact_icon} {item.impact}",
            f"- **Details**: {item.details}",
            "",
        ])

    return "\n".join(lines)


def format_quick_wins(wins: list[ActionItem], url: str) -> str:
    """Format quick wins into a readable string."""
    lines = [
        f"# Quick Wins: {url}",
        "*Top 5 easiest fixes with highest impact*",
        "",
    ]

    for win in wins:
        effort_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(win.effort, "⚪")
        impact_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(win.impact, "⚪")
        lines.extend([
            f"## #{win.priority}: {win.description}",
            f"- **Effort**: {effort_icon} {win.effort} | **Impact**: {impact_icon} {win.impact}",
            f"- {win.details}",
            "",
        ])

    return "\n".join(lines)


def format_seo_score(score: SeoScore, url: str) -> str:
    """Format an SEO score into a readable string."""
    grade = _score_to_grade(score.overall)

    lines = [
        f"# SEO Score: {url}",
        f"## Overall: {score.overall}/100 ({grade})",
        "",
        "| Dimension | Score | Max |",
        "|-----------|-------|-----|",
        f"| Title | {score.title_score} | 15 |",
        f"| Meta Description | {score.meta_score} | 10 |",
        f"| Headings | {score.headings_score} | 15 |",
        f"| Content Depth | {score.content_score} | 20 |",
        f"| Links | {score.links_score} | 10 |",
        f"| Images | {score.images_score} | 10 |",
        f"| Schema | {score.schema_score} | 10 |",
        f"| Technical | {score.technical_score} | 10 |",
    ]

    return "\n".join(lines)


# ─── Search Intent Classification ───────────────────────────────────────────


def classify_search_intent(keyword: str, serp_response: SerpResponse) -> SearchIntentResult:
    """Classify a keyword's search intent based on SERP signals.

    Uses SERP features, keyword patterns, and result types to determine
    whether the intent is informational, navigational, transactional,
    or commercial.

    Args:
        keyword: The keyword to classify.
        serp_response: SERP data for the keyword.

    Returns:
        SearchIntentResult with intent type, confidence, and reasoning.
    """
    kw_lower = keyword.lower().strip()
    signals = []
    scores = {
        "informational": 0,
        "navigational": 0,
        "transactional": 0,
        "commercial": 0,
    }

    # --- Keyword pattern signals ---
    info_patterns = [
        r"\bhow\b", r"\bwhat\b", r"\bwhy\b", r"\bwhen\b", r"\bwhere\b",
        r"\bwho\b", r"\bguide\b", r"\btutorial\b", r"\btips\b",
        r"\bexplain\b", r"\bdefinition\b", r"\bmean(s|ing)?\b",
        r"\bexample(s)?\b", r"\blearn\b",
    ]
    for pattern in info_patterns:
        if re.search(pattern, kw_lower):
            scores["informational"] += 20
            signals.append(f"Keyword contains question/informational word")
            break

    transactional_patterns = [
        r"\bbuy\b", r"\bpurchase\b", r"\border\b", r"\bprice\b",
        r"\bcheap\b", r"\bdeal(s)?\b", r"\bdiscount\b", r"\bcoupon\b",
        r"\bshop(ping)?\b", r"\bfor sale\b", r"\bsubscri(be|ption)\b",
        r"\bdownload\b", r"\bsign up\b", r"\bfree trial\b",
    ]
    for pattern in transactional_patterns:
        if re.search(pattern, kw_lower):
            scores["transactional"] += 25
            signals.append(f"Keyword contains transactional word")
            break

    commercial_patterns = [
        r"\bbest\b", r"\btop\b", r"\breview(s)?\b", r"\bcompare\b",
        r"\bcomparison\b", r"\bvs\b", r"\bversus\b", r"\balternative(s)?\b",
        r"\brecommend(ed|ation)?\b", r"\brated\b", r"\branking\b",
    ]
    for pattern in commercial_patterns:
        if re.search(pattern, kw_lower):
            scores["commercial"] += 25
            signals.append(f"Keyword contains commercial/comparison word")
            break

    # --- SERP feature signals ---
    if not serp_response.error:
        feature_types = {f.type for f in serp_response.serp_features}

        if "featured_snippet" in feature_types:
            scores["informational"] += 15
            signals.append("Featured snippet present")

        if "people_also_ask" in feature_types:
            scores["informational"] += 10
            signals.append("People Also Ask present")

        if "knowledge_panel" in feature_types:
            scores["navigational"] += 15
            signals.append("Knowledge panel present")

        if "shopping_results" in feature_types:
            scores["transactional"] += 20
            signals.append("Shopping results present")

        if "local_pack" in feature_types:
            scores["transactional"] += 10
            signals.append("Local pack present")

        if "video_carousel" in feature_types:
            scores["informational"] += 5
            signals.append("Video carousel present")

    # --- Result snippet analysis ---
    if not serp_response.error and serp_response.organic_results:
        snippets = " ".join(
            r.snippet.lower() for r in serp_response.organic_results if r.snippet
        )
        if any(w in snippets for w in ["buy", "shop", "price", "$", "€", "£"]):
            scores["transactional"] += 10
            signals.append("Snippets contain purchase-related language")
        if any(w in snippets for w in ["best", "review", "top", "compare"]):
            scores["commercial"] += 10
            signals.append("Snippets contain comparison language")
        if any(w in snippets for w in ["how to", "guide", "learn", "what is"]):
            scores["informational"] += 10
            signals.append("Snippets contain informational language")

    # --- Determine winner ---
    if all(v == 0 for v in scores.values()):
        # Default: informational if no signals
        scores["informational"] = 10
        signals.append("No strong signals detected, defaulting to informational")

    intent = max(scores, key=scores.get)
    max_score = scores[intent]
    total_score = sum(scores.values()) or 1
    confidence = min(int((max_score / total_score) * 100), 100)

    # Recommended content type
    content_types = {
        "informational": "Blog post, guide, tutorial, or explainer article",
        "navigational": "Brand/product landing page with clear navigation",
        "transactional": "Product page, pricing page, or sign-up/download page",
        "commercial": "Comparison article, review roundup, or 'best of' listicle",
    }

    return SearchIntentResult(
        keyword=keyword,
        intent=intent,
        confidence=confidence,
        reasoning=f"Classified as {intent} based on: {'; '.join(signals)}.",
        recommended_content_type=content_types.get(intent, ""),
        serp_signals=signals,
    )


def format_search_intent(result: SearchIntentResult) -> str:
    """Format a SearchIntentResult into a readable string for Claude."""
    intent_icon = {
        "informational": "📚",
        "navigational": "🧭",
        "transactional": "💰",
        "commercial": "🔍",
    }
    icon = intent_icon.get(result.intent, "❓")

    lines = [
        f"# Search Intent: \"{result.keyword}\"",
        f"## {icon} Intent: {result.intent.upper()}",
        f"**Confidence**: {result.confidence}%",
        "",
        f"**Reasoning**: {result.reasoning}",
        "",
        f"**Recommended Content Type**: {result.recommended_content_type}",
        "",
    ]

    if result.serp_signals:
        lines.append("## SERP Signals")
        for signal in result.serp_signals:
            lines.append(f"- {signal}")
    
    return "\n".join(lines)


# ─── Private Helpers ─────────────────────────────────────────────────────────


def _avg(values: list[int | float]) -> float:
    """Calculate average, returning 0 for empty lists."""
    return sum(values) / len(values) if values else 0


def _classify_gap(gap: GapDimension) -> tuple[str, str]:
    """Classify a gap into effort and impact levels."""
    high_impact_dims = {
        "Title Tag", "Meta Description", "H1 Tag",
        "Content Depth (Word Count)", "FAQ Section", "Schema Markup",
    }
    easy_dims = {
        "Title Tag", "Title Tag Length", "Meta Description",
        "H1 Tag", "Open Graph Tags", "Image Alt Text",
    }

    impact = "High" if gap.dimension in high_impact_dims else ("Medium" if gap.severity != "low" else "Low")
    effort = "Easy" if gap.dimension in easy_dims else ("Hard" if "Content" in gap.dimension else "Medium")

    return effort, impact


def _categorize_gap(dimension: str) -> str:
    """Categorize a gap dimension into a category."""
    categories = {
        "Title Tag": "meta",
        "Title Tag Length": "meta",
        "Meta Description": "meta",
        "Open Graph Tags": "meta",
        "H1 Tag": "structure",
        "H2 Subheadings": "structure",
        "H3 Subheadings": "structure",
        "Content Depth (Word Count)": "content",
        "Internal Links": "content",
        "External Links": "content",
        "Images": "content",
        "Image Alt Text": "content",
        "FAQ Section": "schema",
        "Schema Markup": "schema",
    }
    return categories.get(dimension, "technical")


def _score_to_grade(score: int) -> str:
    """Convert a numeric score to a letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"
