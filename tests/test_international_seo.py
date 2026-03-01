import pytest
from unittest.mock import patch
from models import InternationalSeoReport, HreflangData
from international_seo import analyze_international_seo, format_international_report

@pytest.fixture
def mock_html_valid_hreflang():
    return """
    <html lang="en-US">
        <head>
            <link rel="alternate" hreflang="en-US" href="http://test.com" />
            <link rel="alternate" hreflang="es-ES" href="http://test.com/es" />
            <link rel="alternate" hreflang="x-default" href="http://test.com" />
        </head>
    </html>
    """

@pytest.fixture
def mock_html_missing_hreflang():
    return "<html><head><title>No Schema</title></head><body>No media here</body></html>"

@pytest.fixture
def mock_html_invalid_hreflang():
    return """
    <html lang="en">
        <head>
            <link rel="alternate" hreflang="es" href="http://test.com/es" />
            <!-- Missing self-referencing and x-default -->
        </head>
    </html>
    """
    
@pytest.mark.asyncio
@patch('international_seo.crawl_page')
async def test_analyze_international_seo_valid(mock_crawl, mock_html_valid_hreflang):
    mock_crawl.return_value = mock_html_valid_hreflang
    report = await analyze_international_seo("http://test.com")
    
    assert report.html_lang == "en-US"
    assert len(report.hreflang_tags) == 3
    assert report.has_self_referencing is True
    assert report.has_x_default is True
    assert "well-configured" in report.recommendations

@pytest.mark.asyncio
@patch('international_seo.crawl_page')
async def test_analyze_international_seo_missing(mock_crawl, mock_html_missing_hreflang):
    mock_crawl.return_value = mock_html_missing_hreflang
    report = await analyze_international_seo("http://test.com")
    
    assert report.html_lang == ""
    assert len(report.hreflang_tags) == 0
    assert "Missing `<html lang>`" in report.recommendations

@pytest.mark.asyncio
@patch('international_seo.crawl_page')
async def test_analyze_international_seo_invalid(mock_crawl, mock_html_invalid_hreflang):
    mock_crawl.return_value = mock_html_invalid_hreflang
    report = await analyze_international_seo("http://test.com")
    
    assert report.html_lang == "en"
    assert len(report.hreflang_tags) == 1
    assert report.has_self_referencing is False
    assert report.has_x_default is False
    assert "Missing `x-default`" in report.recommendations
    assert "Missing self-referencing" in report.recommendations

def test_format_international_report():
    report = InternationalSeoReport("http://test.com", "en", [
         HreflangData("http://test.com", "en", "", False)
    ], False, False, "Test warning")
                                
    formatted = format_international_report(report)
    assert 'International SEO Analysis' in formatted
    assert 'Primary Language' in formatted 
    assert 'Test warning' in formatted
