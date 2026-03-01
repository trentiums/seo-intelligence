import pytest
from models import LocalRankingResult, LocalSeoReport, GeoTag, CitationOpportunity
from local_seo import generate_geo_tags, generate_citation_list, format_geo_tags, format_citations, format_local_seo_report

def test_generate_geo_tags():
    tags = generate_geo_tags("40.7128", "-74.0060", "US-NY", "New York")
    assert "40.7128" in tags.html_tags
    assert "US-NY" in tags.html_tags
    assert "<meta name=\"geo.region\"" in tags.html_tags

def test_generate_citation_list():
    citations = generate_citation_list("Law Firm", "Test Law", "123 Main St", "555-0100")
    assert len(citations) > 5
    domains = [c.domain for c in citations]
    assert "avvo.com" in domains
    assert "yelp.com" in domains
    
    assert "Test Law\n123 Main St" in citations[0].recommended_nap

def test_format_local_seo_report():
    report = LocalSeoReport("Test Biz", "Austin, TX")
    report.rankings.append(LocalRankingResult("coffee", "Austin, TX", 2, "Test Biz Coffee", 4.5, 100))
    report.rankings.append(LocalRankingResult("cafe", "Austin, TX", 0, "Test Biz", error="Not found in Local 3-Pack"))
    
    formatted = format_local_seo_report(report)
    assert 'Rank #2' in formatted
    assert 'Not found in Local 3-Pack' in formatted
    assert 'Test Biz' in formatted
