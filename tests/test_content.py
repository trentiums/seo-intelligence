"""Unit tests for content strategy module — briefs, clustering, cannibalization."""

import pytest

from content import (
    generate_content_brief,
    cluster_keywords,
    detect_cannibalization,
    format_content_brief,
    format_keyword_clusters,
    format_cannibalization_report,
)
from models import (
    PageAnalysis,
    HeadingInfo,
    FAQItem,
    SerpResponse,
    SerpResult,
    SerpFeature,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _make_competitor_page(url, word_count=1200, headings=None, faqs=None):
    """Create a competitor page for testing."""
    if headings is None:
        headings = [
            HeadingInfo(level=1, text="Main Heading"),
            HeadingInfo(level=2, text="Getting Started"),
            HeadingInfo(level=2, text="Best Practices"),
            HeadingInfo(level=3, text="Tip 1"),
        ]
    return PageAnalysis(
        url=url,
        title=f"Guide to Topic — {url}",
        word_count=word_count,
        headings=headings,
        h1_count=1,
        h2_count=sum(1 for h in headings if h.level == 2),
        h3_count=sum(1 for h in headings if h.level == 3),
        faqs=faqs or [],
        has_faq_section=bool(faqs),
    )


def _make_serp_response(keyword, urls, paa=None):
    """Create a SerpResponse for testing."""
    results = [
        SerpResult(position=i + 1, title=f"Result {i + 1}", url=url, snippet=f"Snippet for {keyword}")
        for i, url in enumerate(urls)
    ]
    return SerpResponse(
        keyword=keyword,
        organic_results=results,
        people_also_ask=paa or [],
        total_results=100000,
    )


# ─── Content Brief Tests ────────────────────────────────────────────────────


class TestGenerateContentBrief:
    """Test content brief generation."""

    def test_brief_generates_title(self):
        pages = [_make_competitor_page(f"https://site{i}.com") for i in range(3)]
        serp = _make_serp_response("coffee brewing", [p.url for p in pages])
        brief = generate_content_brief("coffee brewing", serp, pages)

        assert brief.keyword == "coffee brewing"
        assert len(brief.suggested_title) > 0

    def test_brief_word_count_target(self):
        pages = [
            _make_competitor_page("https://a.com", word_count=1000),
            _make_competitor_page("https://b.com", word_count=1500),
            _make_competitor_page("https://c.com", word_count=1200),
        ]
        serp = _make_serp_response("topic", [p.url for p in pages])
        brief = generate_content_brief("topic", serp, pages)

        # Average is ~1233, target should be ~15% more
        assert brief.competitor_avg_word_count > 0
        assert brief.target_word_count > brief.competitor_avg_word_count

    def test_brief_extracts_common_headings(self):
        shared_headings = [
            HeadingInfo(level=1, text="Main"),
            HeadingInfo(level=2, text="Getting Started"),
            HeadingInfo(level=2, text="Best Practices"),
        ]
        pages = [_make_competitor_page(f"https://s{i}.com", headings=shared_headings) for i in range(3)]
        serp = _make_serp_response("topic", [p.url for p in pages])
        brief = generate_content_brief("topic", serp, pages)

        assert len(brief.suggested_headings) > 0

    def test_brief_includes_paa_questions(self):
        pages = [_make_competitor_page(f"https://s{i}.com") for i in range(2)]
        paa = ["How does this work?", "What are the benefits?"]
        serp = _make_serp_response("topic", [p.url for p in pages], paa=paa)
        brief = generate_content_brief("topic", serp, pages)

        assert len(brief.questions_to_answer) >= 2
        assert "How does this work?" in brief.questions_to_answer

    def test_brief_includes_competitor_faqs(self):
        faqs = [FAQItem(question="Is it safe?", answer="Yes.")]
        pages = [_make_competitor_page("https://a.com", faqs=faqs)]
        serp = _make_serp_response("topic", ["https://a.com"])
        brief = generate_content_brief("topic", serp, pages)

        assert "Is it safe?" in brief.questions_to_answer

    def test_brief_no_competitors_returns_error(self):
        serp = _make_serp_response("topic", [])
        brief = generate_content_brief("topic", serp, [])

        assert brief.error != ""

    def test_brief_includes_competitor_urls(self):
        pages = [_make_competitor_page(f"https://s{i}.com") for i in range(2)]
        serp = _make_serp_response("topic", [p.url for p in pages])
        brief = generate_content_brief("topic", serp, pages)

        assert len(brief.competitor_urls) == 2


# ─── Keyword Clustering Tests ───────────────────────────────────────────────


class TestKeywordClustering:
    """Test keyword clustering by SERP overlap."""

    def test_clusters_keywords_with_shared_urls(self):
        keywords = ["cold brew coffee", "cold brew recipe", "iced coffee"]
        serps = [
            _make_serp_response("cold brew coffee", [
                "https://a.com/cold-brew",
                "https://b.com/cold-brew",
                "https://c.com/guide",
            ]),
            _make_serp_response("cold brew recipe", [
                "https://a.com/cold-brew",
                "https://b.com/cold-brew",
                "https://d.com/recipe",
            ]),
            _make_serp_response("iced coffee", [
                "https://e.com/iced",
                "https://f.com/iced",
                "https://g.com/iced",
            ]),
        ]

        clusters = cluster_keywords(keywords, serps)
        assert len(clusters) >= 2  # At least 2 clusters (cold brew group + iced coffee)

        # Cold brew keywords should be clustered together
        cold_brew_cluster = None
        for c in clusters:
            if "cold brew" in c.primary_keyword.lower():
                cold_brew_cluster = c
                break

        assert cold_brew_cluster is not None
        # Either primary is cold brew coffee with cold brew recipe as related,
        # or vice versa
        all_kws = [cold_brew_cluster.primary_keyword] + cold_brew_cluster.related_keywords
        cold_brew_kws = [k for k in all_kws if "cold brew" in k.lower()]
        assert len(cold_brew_kws) >= 2

    def test_no_clusters_for_unique_serps(self):
        keywords = ["python programming", "yoga classes"]
        serps = [
            _make_serp_response("python programming", [
                "https://python.org",
                "https://learnpython.com",
            ]),
            _make_serp_response("yoga classes", [
                "https://yoga.com",
                "https://yogajournal.com",
            ]),
        ]

        clusters = cluster_keywords(keywords, serps)
        # Each keyword should be its own cluster (no overlap)
        assert len(clusters) == 2
        for c in clusters:
            assert len(c.related_keywords) == 0

    def test_empty_keywords_returns_empty(self):
        clusters = cluster_keywords([], [])
        assert clusters == []

    def test_mismatched_lengths_returns_empty(self):
        clusters = cluster_keywords(["a", "b"], [_make_serp_response("a", [])])
        assert clusters == []

    def test_cluster_recommends_page_type(self):
        keywords = ["topic"]
        serps = [_make_serp_response("topic", ["https://a.com"])]
        clusters = cluster_keywords(keywords, serps)

        assert len(clusters) == 1
        assert clusters[0].recommended_page_type != ""


# ─── Cannibalization Detection Tests ─────────────────────────────────────────


class TestCannibalizationDetection:
    """Test keyword cannibalization detection."""

    def test_detects_cannibalization(self):
        keywords = ["coffee maker"]
        serps = [
            _make_serp_response("coffee maker", [
                "https://mysite.com/coffee-makers",
                "https://other.com/best-coffee",
                "https://mysite.com/reviews/coffee",
            ]),
        ]

        issues = detect_cannibalization("mysite.com", keywords, serps)
        assert len(issues) == 1
        assert issues[0].keyword == "coffee maker"
        assert len(issues[0].conflicting_urls) == 2

    def test_no_cannibalization_when_single_page(self):
        keywords = ["coffee maker"]
        serps = [
            _make_serp_response("coffee maker", [
                "https://mysite.com/coffee",
                "https://other.com/coffee",
                "https://another.com/coffee",
            ]),
        ]

        issues = detect_cannibalization("mysite.com", keywords, serps)
        assert len(issues) == 0

    def test_no_cannibalization_when_domain_absent(self):
        keywords = ["coffee maker"]
        serps = [
            _make_serp_response("coffee maker", [
                "https://other.com/coffee",
                "https://another.com/coffee",
            ]),
        ]

        issues = detect_cannibalization("mysite.com", keywords, serps)
        assert len(issues) == 0

    def test_severity_high_for_3_plus_pages(self):
        keywords = ["topic"]
        serps = [
            _make_serp_response("topic", [
                "https://mysite.com/page1",
                "https://other.com/page",
                "https://mysite.com/page2",
                "https://mysite.com/page3",
            ]),
        ]

        issues = detect_cannibalization("mysite.com", keywords, serps)
        assert len(issues) == 1
        assert issues[0].severity == "high"

    def test_handles_www_prefix(self):
        keywords = ["topic"]
        serps = [
            _make_serp_response("topic", [
                "https://www.mysite.com/page1",
                "https://other.com/page",
                "https://www.mysite.com/page2",
            ]),
        ]

        issues = detect_cannibalization("mysite.com", keywords, serps)
        assert len(issues) == 1

    def test_recommendation_present(self):
        keywords = ["topic"]
        serps = [
            _make_serp_response("topic", [
                "https://mysite.com/a",
                "https://mysite.com/b",
            ]),
        ]

        issues = detect_cannibalization("mysite.com", keywords, serps)
        assert len(issues) == 1
        assert len(issues[0].recommendation) > 0


# ─── Formatter Tests ─────────────────────────────────────────────────────────


class TestFormatters:
    """Test content module formatters."""

    def test_format_content_brief(self):
        pages = [_make_competitor_page(f"https://s{i}.com") for i in range(2)]
        serp = _make_serp_response("topic", [p.url for p in pages])
        brief = generate_content_brief("topic", serp, pages)
        output = format_content_brief(brief)

        assert "topic" in output.lower()
        assert "Target Word Count" in output

    def test_format_content_brief_error(self):
        serp = _make_serp_response("topic", [])
        brief = generate_content_brief("topic", serp, [])
        output = format_content_brief(brief)
        assert "❌" in output

    def test_format_keyword_clusters(self):
        keywords = ["a", "b"]
        serps = [
            _make_serp_response("a", ["https://x.com"]),
            _make_serp_response("b", ["https://y.com"]),
        ]
        clusters = cluster_keywords(keywords, serps)
        output = format_keyword_clusters(clusters)
        assert "Cluster" in output

    def test_format_empty_clusters(self):
        output = format_keyword_clusters([])
        assert "No keyword clusters" in output

    def test_format_cannibalization_clean(self):
        output = format_cannibalization_report([])
        assert "✅" in output
        assert "No keyword cannibalization" in output

    def test_format_cannibalization_issues(self):
        keywords = ["topic"]
        serps = [
            _make_serp_response("topic", [
                "https://mysite.com/a",
                "https://mysite.com/b",
            ]),
        ]
        issues = detect_cannibalization("mysite.com", keywords, serps)
        output = format_cannibalization_report(issues)
        assert "Cannibalization" in output
        assert "topic" in output
