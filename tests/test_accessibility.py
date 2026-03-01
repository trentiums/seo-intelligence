import pytest
from unittest.mock import patch
from models import AccessibilityReport, WcagViolation
from accessibility_seo import analyze_accessibility, format_accessibility_report

@pytest.fixture
def mock_html_accessible():
    return """
    <html lang="en">
        <head>
            <title>My Accessible Page</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <img src="logo.png" alt="Company Logo" />
            <a href="/login" aria-label="Login">Login</a>
            <button>Click Here</button>
        </body>
    </html>
    """

@pytest.fixture
def mock_html_violations():
    return """
    <html>
        <head>
            <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1">
        </head>
        <body>
            <img src="image1.png" />
            <img src="image2.png" />
            <a href="/contact"></a>
            <button></button>
        </body>
    </html>
    """

@pytest.mark.asyncio
@patch('accessibility_seo.crawl_page')
async def test_analyze_accessibility_perfect(mock_crawl, mock_html_accessible):
    mock_crawl.return_value = mock_html_accessible
    report = await analyze_accessibility("http://test.com")
    
    assert report.score == 100
    assert len(report.violations) == 0

@pytest.mark.asyncio
@patch('accessibility_seo.crawl_page')
async def test_analyze_accessibility_violations(mock_crawl, mock_html_violations):
    mock_crawl.return_value = mock_html_violations
    report = await analyze_accessibility("http://test.com")
    
    assert report.score < 100
    assert len(report.violations) > 0
    
    rule_ids = [v.rule_id for v in report.violations]
    assert "html-has-lang" in rule_ids
    assert "image-alt" in rule_ids
    assert "empty-a" in rule_ids
    assert "empty-button" in rule_ids
    assert "meta-viewport" in rule_ids
    assert "document-title" in rule_ids

def test_format_accessibility_report():
    report = AccessibilityReport("http://test.com", 50, 5, [
        WcagViolation("test-rule", "Test description", "Error", "<div></div>")
    ])
    
    formatted = format_accessibility_report(report)
    assert 'Accessibility (A11y) & UX Audit' in formatted
    assert 'Score: 50/100' in formatted
    assert 'Test description' in formatted
    assert '<div></div>' in formatted
