"""Unit tests for SEO scoring, gap analysis, plan generation, and search intent."""

import pytest

from analyzer import calculate_seo_score, compare_pages, generate_action_plan, find_quick_wins, classify_search_intent
from models import PageAnalysis, HeadingInfo, ImageInfo, FAQItem, SerpResponse, SerpResult, SerpFeature


# ─── Test Fixtures ───────────────────────────────────────────────────────────


def _make_good_page() -> PageAnalysis:
    """Create a well-optimized page for testing."""
    return PageAnalysis(
        url="https://example.com/good-page",
        title="Best Coffee Makers 2026 — Expert Reviews & Guide",
        meta_description="Discover the 10 best coffee makers of 2026. We tested 50+ models. Read expert reviews, compare prices, and find your perfect coffee maker.",
        canonical_url="https://example.com/good-page",
        headings=[
            HeadingInfo(level=1, text="Best Coffee Makers 2026"),
            HeadingInfo(level=2, text="Top Picks"),
            HeadingInfo(level=3, text="Best Overall"),
            HeadingInfo(level=3, text="Best Budget"),
            HeadingInfo(level=2, text="How We Test"),
            HeadingInfo(level=2, text="Buying Guide"),
            HeadingInfo(level=3, text="What to Look For"),
        ],
        h1_count=1,
        h2_count=3,
        h3_count=3,
        word_count=1800,
        internal_links=[],
        external_links=[],
        internal_link_count=8,
        external_link_count=3,
        images=[
            ImageInfo(src="/img1.jpg", alt="Coffee maker photo", has_alt=True),
            ImageInfo(src="/img2.jpg", alt="Comparison chart", has_alt=True),
        ],
        total_images=2,
        images_with_alt=2,
        images_without_alt=0,
        image_alt_coverage=100.0,
        faqs=[
            FAQItem(question="What is the best coffee maker?", answer="The Breville Precision Brewer."),
        ],
        has_faq_section=True,
        schema_types=["Article", "FAQPage"],
        has_schema=True,
        has_og_tags=True,
        has_viewport_meta=True,
        has_lang_attribute=True,
        has_charset=True,
    )


def _make_poor_page() -> PageAnalysis:
    """Create a poorly optimized page for testing."""
    return PageAnalysis(
        url="https://example.com/poor-page",
        title="Page",
        meta_description="",
        headings=[],
        h1_count=0,
        h2_count=0,
        h3_count=0,
        word_count=50,
        internal_link_count=0,
        external_link_count=0,
        total_images=3,
        images_with_alt=0,
        images_without_alt=3,
        images=[
            ImageInfo(src="/a.jpg", alt="", has_alt=False),
            ImageInfo(src="/b.jpg", alt="", has_alt=False),
            ImageInfo(src="/c.jpg", alt="", has_alt=False),
        ],
        image_alt_coverage=0.0,
        has_faq_section=False,
        has_schema=False,
        has_og_tags=False,
        has_viewport_meta=False,
        has_lang_attribute=False,
        has_charset=False,
    )


# ─── SEO Score Tests ─────────────────────────────────────────────────────────


class TestSeoScoring:
    """Test the SEO scoring algorithm."""

    def test_good_page_scores_high(self):
        page = _make_good_page()
        score = calculate_seo_score(page)
        assert score.overall >= 75, f"Good page scored only {score.overall}"

    def test_poor_page_scores_low(self):
        page = _make_poor_page()
        score = calculate_seo_score(page)
        assert score.overall <= 30, f"Poor page scored {score.overall}"

    def test_score_range(self):
        page = _make_good_page()
        score = calculate_seo_score(page)
        assert 0 <= score.overall <= 100

    def test_title_scoring_optimal_length(self):
        page = PageAnalysis(url="test", title="A" * 50)  # 50 chars — optimal
        score = calculate_seo_score(page)
        assert score.title_score == 15

    def test_title_scoring_missing(self):
        page = PageAnalysis(url="test", title="")
        score = calculate_seo_score(page)
        assert score.title_score == 0

    def test_meta_scoring_optimal_length(self):
        page = PageAnalysis(url="test", meta_description="A" * 140)  # 140 chars — optimal
        score = calculate_seo_score(page)
        assert score.meta_score == 10

    def test_content_scoring_deep_content(self):
        page = PageAnalysis(url="test", word_count=2000)
        score = calculate_seo_score(page)
        assert score.content_score == 20

    def test_content_scoring_thin(self):
        page = PageAnalysis(url="test", word_count=50)
        score = calculate_seo_score(page)
        assert score.content_score == 0

    def test_heading_scoring_perfect(self):
        page = PageAnalysis(
            url="test",
            h1_count=1,
            h2_count=3,
            h3_count=2,
            headings=[
                HeadingInfo(level=1, text="Title"),
                HeadingInfo(level=2, text="Section 1"),
                HeadingInfo(level=2, text="Section 2"),
                HeadingInfo(level=2, text="Section 3"),
                HeadingInfo(level=3, text="Sub 1"),
                HeadingInfo(level=3, text="Sub 2"),
            ],
        )
        score = calculate_seo_score(page)
        assert score.headings_score == 15

    def test_schema_scoring_with_faq(self):
        page = PageAnalysis(
            url="test",
            schema_types=["Article", "FAQPage"],
            has_schema=True,
            has_faq_section=True,
        )
        score = calculate_seo_score(page)
        assert score.schema_score == 10  # 8 for 2 schemas + 2 for FAQ, capped at 10

    def test_breakdown_dict_populated(self):
        page = _make_good_page()
        score = calculate_seo_score(page)
        expected_keys = {"title", "meta_description", "headings", "content", "links", "images", "schema", "technical"}
        assert expected_keys == set(score.breakdown.keys())


# ─── Gap Analysis Tests ─────────────────────────────────────────────────────


class TestGapAnalysis:
    """Test competitor gap comparison."""

    def test_gaps_detected(self):
        user = _make_poor_page()
        competitors = [_make_good_page(), _make_good_page()]
        report = compare_pages(user, competitors)
        assert len(report.gaps) > 0

    def test_no_gaps_for_good_page(self):
        user = _make_good_page()
        # Create slightly worse competitors
        comp = _make_good_page()
        comp.word_count = 1500
        report = compare_pages(user, [comp])
        high_severity = [g for g in report.gaps if g.severity == "high"]
        assert len(high_severity) == 0

    def test_word_count_gap(self):
        user = PageAnalysis(url="test", word_count=200)
        comp = PageAnalysis(url="comp", word_count=1500)
        report = compare_pages(user, [comp])
        wc_gaps = [g for g in report.gaps if "Word Count" in g.dimension]
        assert len(wc_gaps) == 1

    def test_missing_title_flagged(self):
        user = PageAnalysis(url="test", title="")
        comp = PageAnalysis(url="comp", title="Great Title Here for SEO")
        report = compare_pages(user, [comp])
        title_gaps = [g for g in report.gaps if "Title" in g.dimension]
        assert len(title_gaps) > 0

    def test_missing_meta_flagged(self):
        user = PageAnalysis(url="test", meta_description="")
        comp = PageAnalysis(url="comp", meta_description="A good description here for testing purposes")
        report = compare_pages(user, [comp])
        meta_gaps = [g for g in report.gaps if "Meta Description" in g.dimension]
        assert len(meta_gaps) == 1

    def test_missing_faq_flagged(self):
        user = PageAnalysis(url="test", has_faq_section=False)
        comp = PageAnalysis(url="comp", has_faq_section=True)
        report = compare_pages(user, [comp])
        faq_gaps = [g for g in report.gaps if "FAQ" in g.dimension]
        assert len(faq_gaps) == 1

    def test_empty_competitors_handled(self):
        user = _make_poor_page()
        report = compare_pages(user, [])
        assert "No competitor" in report.summary

    def test_scores_calculated(self):
        user = _make_poor_page()
        competitors = [_make_good_page()]
        report = compare_pages(user, competitors)
        assert report.user_score < report.competitor_avg_score


# ─── Action Plan Tests ───────────────────────────────────────────────────────


class TestActionPlan:
    """Test ranking plan generation."""

    def test_plan_generated_from_gaps(self):
        user = _make_poor_page()
        competitors = [_make_good_page()]
        gap_report = compare_pages(user, competitors)
        gap_report.keyword = "best coffee maker"
        plan = generate_action_plan(gap_report)
        assert len(plan.action_items) > 0

    def test_priorities_assigned(self):
        user = _make_poor_page()
        competitors = [_make_good_page()]
        gap_report = compare_pages(user, competitors)
        gap_report.keyword = "test"
        plan = generate_action_plan(gap_report)
        priorities = [a.priority for a in plan.action_items]
        assert priorities == sorted(priorities)
        assert priorities[0] == 1

    def test_high_impact_first(self):
        user = _make_poor_page()
        competitors = [_make_good_page()]
        gap_report = compare_pages(user, competitors)
        gap_report.keyword = "test"
        plan = generate_action_plan(gap_report)
        if len(plan.action_items) >= 2:
            # First item should be High impact
            assert plan.action_items[0].impact == "High"

    def test_estimated_score_reasonable(self):
        user = _make_poor_page()
        competitors = [_make_good_page()]
        gap_report = compare_pages(user, competitors)
        gap_report.keyword = "test"
        plan = generate_action_plan(gap_report)
        assert plan.estimated_score_after > gap_report.user_score
        assert plan.estimated_score_after <= 100


# ─── Quick Wins Tests ────────────────────────────────────────────────────────


class TestQuickWins:
    """Test quick wins finder."""

    def test_poor_page_has_wins(self):
        page = _make_poor_page()
        wins = find_quick_wins(page)
        assert len(wins) > 0
        assert len(wins) <= 5

    def test_good_page_fewer_wins(self):
        page = _make_good_page()
        wins = find_quick_wins(page)
        # Good page may still have some wins but fewer
        poor_page = _make_poor_page()
        poor_wins = find_quick_wins(poor_page)
        assert len(wins) <= len(poor_wins)

    def test_wins_sorted_by_impact(self):
        page = _make_poor_page()
        wins = find_quick_wins(page)
        if len(wins) >= 2:
            impact_order = {"High": 0, "Medium": 1, "Low": 2}
            impact_values = [impact_order.get(w.impact, 1) for w in wins]
            assert impact_values == sorted(impact_values)

    def test_wins_have_priorities(self):
        page = _make_poor_page()
        wins = find_quick_wins(page)
        for i, win in enumerate(wins, 1):
            assert win.priority == i

    def test_missing_title_is_quick_win(self):
        page = PageAnalysis(url="test", title="")
        wins = find_quick_wins(page)
        title_wins = [w for w in wins if "title" in w.description.lower()]
        assert len(title_wins) > 0

    def test_missing_meta_is_quick_win(self):
        page = PageAnalysis(url="test", title="OK Title Here", meta_description="")
        wins = find_quick_wins(page)
        meta_wins = [w for w in wins if "meta description" in w.description.lower()]
        assert len(meta_wins) > 0


# ─── Search Intent Classification Tests ─────────────────────────────────────


def _make_serp(keyword, feature_types=None, snippets=None):
    """Create a SerpResponse with optional features and custom snippets."""
    features = [SerpFeature(type=ft) for ft in (feature_types or [])]
    results = [
        SerpResult(
            position=i + 1,
            title=f"Result {i + 1}",
            url=f"https://site{i}.com",
            snippet=snippets[i] if snippets and i < len(snippets) else f"About {keyword}",
        )
        for i in range(3)
    ]
    return SerpResponse(
        keyword=keyword,
        organic_results=results,
        serp_features=features,
        total_results=100000,
    )


class TestSearchIntentClassification:
    """Test search intent classification logic."""

    def test_transactional_intent(self):
        serp = _make_serp(
            "buy coffee maker online",
            feature_types=["shopping_results"],
            snippets=["Shop the best prices now", "Buy online at $49", "Free shipping deals"],
        )
        result = classify_search_intent("buy coffee maker online", serp)
        assert result.intent == "transactional"

    def test_informational_intent(self):
        serp = _make_serp(
            "how to make cold brew coffee",
            feature_types=["featured_snippet", "people_also_ask"],
            snippets=["Learn how to make cold brew", "Step-by-step guide", "What is cold brew"],
        )
        result = classify_search_intent("how to make cold brew coffee", serp)
        assert result.intent == "informational"

    def test_navigational_intent(self):
        serp = _make_serp(
            "starbucks",
            feature_types=["knowledge_panel"],
        )
        result = classify_search_intent("starbucks", serp)
        assert result.intent == "navigational"

    def test_commercial_intent(self):
        serp = _make_serp(
            "best coffee maker 2026",
            snippets=["Top 10 best coffee makers reviewed", "Compare the best models", "Our expert review"],
        )
        result = classify_search_intent("best coffee maker 2026", serp)
        assert result.intent == "commercial"

    def test_intent_confidence_range(self):
        serp = _make_serp("random query")
        result = classify_search_intent("random query", serp)
        assert 0 <= result.confidence <= 100
        assert result.intent in ("informational", "navigational", "transactional", "commercial")
        assert len(result.recommended_content_type) > 0

