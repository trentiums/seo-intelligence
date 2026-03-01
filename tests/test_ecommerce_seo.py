import pytest
from unittest.mock import patch
from models import EcommerceSeoReport, ProductSchemaResult
from ecommerce_seo import analyze_product_seo, format_ecommerce_report

@pytest.fixture
def mock_html_valid_schema():
    return """
    <html>
        <head>
            <script type="application/ld+json">
            {
              "@context": "https://schema.org/",
              "@type": "Product",
              "name": "Executive Anvil",
              "image": "https://example.com/anvil.png",
              "description": "Sleeker than ACME's Classic Anvil.",
              "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.4",
                "reviewCount": "89"
              },
              "offers": {
                "@type": "Offer",
                "priceCurrency": "USD",
                "price": "119.99",
                "availability": "https://schema.org/InStock"
              }
            }
            </script>
        </head>
    </html>
    """

@pytest.fixture
def mock_html_missing_schema():
    return "<html><head><title>No Schema</title></head><body>Product</body></html>"

@pytest.fixture
def mock_html_partial_schema():
     return """
    <html>
        <head>
            <script type="application/ld+json">
            {
              "@context": "https://schema.org/",
              "@type": "Product",
              "name": "Executive Anvil"
            }
            </script>
        </head>
    </html>
    """

@pytest.mark.asyncio
@patch('ecommerce_seo.crawl_page')
async def test_analyze_product_seo_valid(mock_crawl, mock_html_valid_schema):
    mock_crawl.return_value = mock_html_valid_schema
    report = await analyze_product_seo("http://test.com")
    
    assert report.schema_status == "Valid"
    assert report.product_name == "Executive Anvil"
    assert report.schema_details.price == 119.99
    assert report.schema_details.currency == "USD"
    assert report.schema_details.rating == 4.4
    assert len(report.schema_details.missing_fields) == 0

@pytest.mark.asyncio
@patch('ecommerce_seo.crawl_page')
async def test_analyze_product_seo_missing(mock_crawl, mock_html_missing_schema):
    mock_crawl.return_value = mock_html_missing_schema
    report = await analyze_product_seo("http://test.com")
    
    assert report.schema_status == "Missing"
    assert "No Product schema found" in report.recommendations

@pytest.mark.asyncio
@patch('ecommerce_seo.crawl_page')
async def test_analyze_product_seo_partial(mock_crawl, mock_html_partial_schema):
    mock_crawl.return_value = mock_html_partial_schema
    report = await analyze_product_seo("http://test.com")
    
    assert report.schema_status == "Incomplete"
    assert "offers" in report.schema_details.missing_fields
    assert "aggregateRating" in report.schema_details.missing_fields

def test_format_ecommerce_report():
    report = EcommerceSeoReport("http://test.com", "Test Product", "Incomplete", 
                                ProductSchemaResult("Test Product", 10.0, "USD", "InStock", 0.0, 0, ["aggregateRating"]))
                                
    formatted = format_ecommerce_report(report)
    assert 'E-commerce Product SEO Analysis' in formatted
    assert '⚠️ Incomplete' in formatted
    assert 'Missing Fields (1)' in formatted
    assert '`aggregateRating`' in formatted
