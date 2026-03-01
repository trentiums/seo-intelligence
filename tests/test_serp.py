"""Unit tests for SERP response parsing (mocked — no real API calls)."""

import pytest

from serp import parse_serp_response, _extract_serp_features
from models import SerpResponse


# ─── Sample SerpAPI Response Fixtures ────────────────────────────────────────

SAMPLE_SERP_RESPONSE = {
    "search_information": {
        "total_results": 1230000000,
        "query_displayed": "best coffee maker",
    },
    "organic_results": [
        {
            "position": 1,
            "title": "The 10 Best Coffee Makers of 2026 | Tested & Reviewed",
            "link": "https://www.example1.com/best-coffee-makers",
            "snippet": "After testing 50+ coffee makers, our top pick is the Breville Precision Brewer.",
            "displayed_link": "www.example1.com › best-coffee-makers",
        },
        {
            "position": 2,
            "title": "Best Coffee Makers 2026 - CNET",
            "link": "https://www.example2.com/coffee-makers",
            "snippet": "We update this list regularly with our latest expert reviews.",
            "displayed_link": "www.example2.com › coffee-makers",
        },
        {
            "position": 3,
            "title": "7 Best Coffee Makers, Tested by Food Experts",
            "link": "https://www.example3.com/coffee",
            "snippet": "Our food experts tested coffee makers for ease of use, brew quality, and value.",
            "displayed_link": "www.example3.com › coffee",
        },
        {
            "position": 4,
            "title": "Best Coffee Machines for Home Use",
            "link": "https://www.example4.com/machines",
            "snippet": "Home coffee machines ranked by performance.",
            "displayed_link": "www.example4.com › machines",
        },
    ],
    "answer_box": {
        "type": "organic_result",
        "title": "Best coffee maker overall",
        "answer": "Breville Precision Brewer",
    },
    "related_questions": [
        {"question": "What is the best coffee maker to buy?"},
        {"question": "Is Keurig better than drip?"},
        {"question": "What coffee maker does Starbucks use?"},
    ],
    "knowledge_graph": {
        "title": "Coffee maker",
        "type": "Kitchen appliance",
    },
    "inline_videos": [
        {"title": "Top 5 Coffee Makers 2026", "link": "https://youtube.com/watch?v=abc"},
    ],
}

MINIMAL_SERP_RESPONSE = {
    "organic_results": [
        {
            "position": 1,
            "title": "Result 1",
            "link": "https://example.com/1",
        },
    ],
}

EMPTY_SERP_RESPONSE = {}

ERROR_SERP_RESPONSE = {
    "error": "Invalid API key",
}


# ─── Tests ───────────────────────────────────────────────────────────────────


class TestParseSerpResponse:
    """Test parsing raw SerpAPI JSON into structured results."""

    def test_organic_results_extracted(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "best coffee maker", num_results=3)
        assert len(response.organic_results) == 3

    def test_organic_result_fields(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "best coffee maker", num_results=1)
        result = response.organic_results[0]
        assert result.position == 1
        assert "Best Coffee Makers" in result.title
        assert result.url == "https://www.example1.com/best-coffee-makers"
        assert "testing" in result.snippet.lower()

    def test_total_results(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "best coffee maker")
        assert response.total_results == 1230000000

    def test_keyword_preserved(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "best coffee maker")
        assert response.keyword == "best coffee maker"

    def test_num_results_limits_output(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "test", num_results=2)
        assert len(response.organic_results) == 2

    def test_people_also_ask(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "test")
        assert len(response.people_also_ask) == 3
        assert "What is the best coffee maker to buy?" in response.people_also_ask

    def test_minimal_response(self):
        response = parse_serp_response(MINIMAL_SERP_RESPONSE, "test")
        assert len(response.organic_results) == 1
        assert response.total_results == 0
        assert len(response.people_also_ask) == 0

    def test_empty_response(self):
        response = parse_serp_response(EMPTY_SERP_RESPONSE, "test")
        assert len(response.organic_results) == 0
        assert response.error == ""

    def test_no_error_for_valid_response(self):
        response = parse_serp_response(SAMPLE_SERP_RESPONSE, "test")
        assert response.error == ""


class TestSerpFeatures:
    """Test SERP feature detection."""

    def test_featured_snippet_detected(self):
        features = _extract_serp_features(SAMPLE_SERP_RESPONSE)
        types = [f.type for f in features]
        assert "featured_snippet" in types

    def test_knowledge_panel_detected(self):
        features = _extract_serp_features(SAMPLE_SERP_RESPONSE)
        types = [f.type for f in features]
        assert "knowledge_panel" in types

    def test_paa_detected(self):
        features = _extract_serp_features(SAMPLE_SERP_RESPONSE)
        types = [f.type for f in features]
        assert "people_also_ask" in types

    def test_video_carousel_detected(self):
        features = _extract_serp_features(SAMPLE_SERP_RESPONSE)
        types = [f.type for f in features]
        assert "video_carousel" in types

    def test_no_features_for_minimal(self):
        features = _extract_serp_features(MINIMAL_SERP_RESPONSE)
        assert len(features) == 0

    def test_no_features_for_empty(self):
        features = _extract_serp_features(EMPTY_SERP_RESPONSE)
        assert len(features) == 0

    def test_multiple_features_detected(self):
        features = _extract_serp_features(SAMPLE_SERP_RESPONSE)
        assert len(features) >= 3  # featured_snippet, knowledge_panel, PAA, video at minimum
