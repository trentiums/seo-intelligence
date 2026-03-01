"""Unit tests for page crawling and HTML parsing."""

import pytest

from crawler import parse_page
from models import PageAnalysis


# ─── Sample HTML Fixtures ────────────────────────────────────────────────────

GOOD_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Best Coffee Makers 2026 | Expert Reviews</title>
    <meta name="description" content="Discover the best coffee makers of 2026. Our experts tested 50+ models to find the top picks for every budget and brewing style.">
    <link rel="canonical" href="https://example.com/best-coffee-makers">
    <meta property="og:title" content="Best Coffee Makers 2026">
    <meta property="og:description" content="Expert-reviewed coffee makers for every budget.">
    <meta property="og:image" content="https://example.com/images/coffee.jpg">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Best Coffee Makers 2026",
        "author": {"@type": "Person", "name": "John Expert"}
    }
    </script>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is the best coffee maker?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "The Breville Precision Brewer is our top pick."
                }
            },
            {
                "@type": "Question",
                "name": "How much should I spend?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Great coffee makers start at around $50."
                }
            }
        ]
    }
    </script>
</head>
<body>
    <h1>Best Coffee Makers 2026</h1>
    <p>We tested over 50 coffee makers to find the best options for every budget and brewing preference. Here are our expert picks after weeks of testing.</p>

    <h2>Top Picks for 2026</h2>
    <p>After extensive testing, these are the coffee makers that stood out from the crowd.</p>

    <h3>Best Overall: Breville Precision Brewer</h3>
    <p>The Breville Precision Brewer offers unmatched versatility and superb coffee quality.</p>
    <img src="/images/breville.jpg" alt="Breville Precision Brewer coffee maker on a kitchen counter">

    <h3>Best Budget: Hamilton Beach FlexBrew</h3>
    <p>For those on a budget, the Hamilton Beach FlexBrew delivers excellent value.</p>
    <img src="/images/hamilton.jpg" alt="Hamilton Beach FlexBrew dual coffee maker">

    <h2>How We Test</h2>
    <p>Our testing process involves multiple rounds of brewing with different coffee beans.</p>

    <h2>Buying Guide</h2>
    <h3>What to Look For</h3>
    <p>When shopping for a coffee maker, consider brew capacity, speed, temperature control, and ease of cleaning.</p>

    <a href="/drip-coffee-makers">Drip Coffee Makers</a>
    <a href="/espresso-machines">Espresso Machines</a>
    <a href="/french-press">French Press Guide</a>
    <a href="https://www.ncausa.org/">National Coffee Association</a>
    <a href="https://www.sca.coffee/">Specialty Coffee Association</a>

    <img src="/images/comparison.jpg" alt="Coffee maker comparison chart">
    <img src="/images/testing.jpg">

    <p>This is additional content to boost the word count of the page for testing purposes. We want to ensure the parser correctly counts all the words on this page accurately.</p>
</body>
</html>
"""

MINIMAL_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Short</title>
</head>
<body>
    <p>Just a few words here.</p>
    <img src="/logo.png">
</body>
</html>
"""

EMPTY_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head></head>
<body></body>
</html>
"""


# ─── Tests ───────────────────────────────────────────────────────────────────


class TestParsePageGoodHTML:
    """Tests for a well-structured SEO page."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.analysis = parse_page(GOOD_PAGE_HTML, "https://example.com/best-coffee-makers")

    def test_title_extraction(self):
        assert self.analysis.title == "Best Coffee Makers 2026 | Expert Reviews"

    def test_meta_description(self):
        assert "best coffee makers" in self.analysis.meta_description.lower()
        assert len(self.analysis.meta_description) > 50

    def test_canonical_url(self):
        assert self.analysis.canonical_url == "https://example.com/best-coffee-makers"

    def test_h1_count(self):
        assert self.analysis.h1_count == 1

    def test_h2_count(self):
        assert self.analysis.h2_count == 3  # Top Picks, How We Test, Buying Guide

    def test_h3_count(self):
        assert self.analysis.h3_count == 3  # Best Overall, Best Budget, What to Look For

    def test_heading_hierarchy(self):
        levels = [h.level for h in self.analysis.headings]
        assert levels[0] == 1  # H1 first
        assert 2 in levels
        assert 3 in levels

    def test_word_count_reasonable(self):
        assert self.analysis.word_count > 50

    def test_internal_links(self):
        assert self.analysis.internal_link_count == 3  # drip, espresso, french press

    def test_external_links(self):
        assert self.analysis.external_link_count == 2  # NCA, SCA

    def test_total_images(self):
        assert self.analysis.total_images == 4  # breville, hamilton, comparison, testing

    def test_images_with_alt(self):
        assert self.analysis.images_with_alt == 3  # breville, hamilton, comparison

    def test_images_without_alt(self):
        assert self.analysis.images_without_alt == 1  # testing.jpg has no alt

    def test_image_alt_coverage(self):
        assert self.analysis.image_alt_coverage == 75.0

    def test_faq_detection(self):
        assert self.analysis.has_faq_section is True
        assert len(self.analysis.faqs) == 2
        assert "best coffee maker" in self.analysis.faqs[0].question.lower()

    def test_schema_types(self):
        assert self.analysis.has_schema is True
        assert "Article" in self.analysis.schema_types
        assert "FAQPage" in self.analysis.schema_types

    def test_og_tags(self):
        assert self.analysis.has_og_tags is True
        assert self.analysis.og_title == "Best Coffee Makers 2026"
        assert self.analysis.og_image == "https://example.com/images/coffee.jpg"

    def test_viewport_meta(self):
        assert self.analysis.has_viewport_meta is True

    def test_lang_attribute(self):
        assert self.analysis.has_lang_attribute is True

    def test_charset(self):
        assert self.analysis.has_charset is True


class TestParsePageMinimalHTML:
    """Tests for a minimal page with poor SEO."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.analysis = parse_page(MINIMAL_PAGE_HTML, "https://example.com/short")

    def test_short_title(self):
        assert self.analysis.title == "Short"

    def test_no_meta_description(self):
        assert self.analysis.meta_description == ""

    def test_no_h1(self):
        assert self.analysis.h1_count == 0

    def test_low_word_count(self):
        assert self.analysis.word_count < 20

    def test_no_faq(self):
        assert self.analysis.has_faq_section is False

    def test_no_schema(self):
        assert self.analysis.has_schema is False

    def test_image_without_alt(self):
        assert self.analysis.total_images == 1
        assert self.analysis.images_without_alt == 1
        assert self.analysis.image_alt_coverage == 0.0


class TestParsePageEmptyHTML:
    """Tests for an effectively empty page."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.analysis = parse_page(EMPTY_PAGE_HTML, "https://example.com/empty")

    def test_no_title(self):
        assert self.analysis.title == ""

    def test_zero_word_count(self):
        assert self.analysis.word_count == 0

    def test_no_headings(self):
        assert len(self.analysis.headings) == 0

    def test_no_links(self):
        assert self.analysis.internal_link_count == 0
        assert self.analysis.external_link_count == 0

    def test_no_images(self):
        assert self.analysis.total_images == 0
