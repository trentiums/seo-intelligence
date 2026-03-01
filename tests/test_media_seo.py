import pytest
from unittest.mock import patch
from models import MediaSeoReport, VideoSchemaResult, SpeakableSchemaResult
from media_seo import analyze_media_seo, format_media_report

@pytest.fixture
def mock_html_valid_media():
    return """
    <html>
        <head>
            <script type="application/ld+json">
            {
              "@context": "https://schema.org/",
              "@type": "VideoObject",
              "name": "How to tie a tie",
              "description": "A step-by-step guide to tying a perfect knot.",
              "thumbnailUrl": "https://example.com/tie.jpg",
              "uploadDate": "2024-03-01T08:00:00+08:00",
              "duration": "PT1M33S",
              "contentUrl": "https://example.com/tie.mp4"
            }
            </script>
            <script type="application/ld+json">
            {
              "@context": "https://schema.org",
              "@type": "Article",
              "name": "How to tie a tie article",
              "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".speakable-text"]
              }
            }
            </script>
        </head>
    </html>
    """

@pytest.fixture
def mock_html_missing_media():
    return "<html><head><title>No Schema</title></head><body>No media here</body></html>"

@pytest.mark.asyncio
@patch('media_seo.crawl_page')
async def test_analyze_media_seo_valid(mock_crawl, mock_html_valid_media):
    mock_crawl.return_value = mock_html_valid_media
    report = await analyze_media_seo("http://test.com")
    
    assert report.video_status == "Valid"
    assert len(report.video_details) == 1
    assert report.video_details[0].name == "How to tie a tie"
    assert len(report.video_details[0].missing_fields) == 0
    
    assert report.speakable_status == "Valid"
    assert report.speakable_details.is_present is True
    assert ".speakable-text" in report.speakable_details.css_selectors

@pytest.mark.asyncio
@patch('media_seo.crawl_page')
async def test_analyze_media_seo_missing(mock_crawl, mock_html_missing_media):
    mock_crawl.return_value = mock_html_missing_media
    report = await analyze_media_seo("http://test.com")
    
    assert report.video_status == "Missing"
    assert report.speakable_status == "Missing"
    assert "No VideoObject schema found" in report.recommendations

def test_format_media_report():
    report = MediaSeoReport("http://test.com", "Missing", [], "Incomplete", SpeakableSchemaResult(True, [], [], ["cssSelector OR xpath"]))
                                
    formatted = format_media_report(report)
    assert 'Media (Video & Voice) SEO Analysis' in formatted
    assert '❌ Missing' in formatted # Video
    assert '⚠️ Incomplete' in formatted # Speakable
    assert 'cssSelector OR xpath' in formatted
