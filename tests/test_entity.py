import pytest
from unittest.mock import patch
from models import EntityAnalysisResult
from entity import verify_entity, format_entity_report
import os

@pytest.fixture
def mock_google_key():
    os.environ["GOOGLE_CLOUD_API_KEY"] = "test_gc"
    yield
    del os.environ["GOOGLE_CLOUD_API_KEY"]

@pytest.fixture
def clean_keys():
    if "GOOGLE_CLOUD_API_KEY" in os.environ:
        del os.environ["GOOGLE_CLOUD_API_KEY"]
    yield

@pytest.mark.asyncio
async def test_verify_entity_no_key(clean_keys):
    results = await verify_entity("coffee")
    assert len(results) == 1
    assert "GOOGLE_CLOUD_API_KEY is not configured" in results[0].error

def test_format_entity_report():
    results = [
        EntityAnalysisResult(
            entity_name="Coffee",
            description="A brewed drink prepared from roasted coffee beans.",
            kg_mid="/m/02vqfm",
            wikipedia_url="https://en.wikipedia.org/wiki/Coffee",
            confidence_score=990.5,
            recommendations="Add sameAs"
        )
    ]
    report = format_entity_report("coffee", results)
    
    assert "Entity SEO" in report
    assert "Coffee" in report
    assert "kg_mid" not in report # we display (MID) instead
    assert "/m/02vqfm" in report
    assert "https://en.wikipedia.org/wiki/Coffee" in report
    assert "Add sameAs" in report
