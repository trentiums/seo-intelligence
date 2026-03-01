import pytest
from unittest.mock import patch
from models import AeoAnalysisResult
from ai_search import analyze_aeo_visibility, format_aeo_report
import os

@pytest.fixture
def mock_keys():
    os.environ["PERPLEXITY_API_KEY"] = "test_px"
    os.environ["OPENAI_API_KEY"] = "test_oa"
    os.environ["SERPAPI_KEY"] = "test_sa"
    yield
    if "PERPLEXITY_API_KEY" in os.environ:
        del os.environ["PERPLEXITY_API_KEY"]
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    if "SERPAPI_KEY" in os.environ:
        del os.environ["SERPAPI_KEY"]

@pytest.fixture
def mock_no_keys():
    keys = ["PERPLEXITY_API_KEY", "OPENAI_API_KEY", "SERPAPI_KEY"]
    backup = {}
    for k in keys:
        if k in os.environ:
            backup[k] = os.environ[k]
            del os.environ[k]
    yield
    for k, v in backup.items():
        os.environ[k] = v

@pytest.mark.asyncio
@patch('ai_search._check_perplexity')
@patch('ai_search._check_openai')
@patch('ai_search._check_sge')
async def test_analyze_aeo_visibility_all_keys(mock_sge, mock_openai, mock_perplexity, mock_keys):
    mock_perplexity.return_value = AeoAnalysisResult("coffee", "Perplexity", True, ["https://example.com/coffee"])
    mock_openai.return_value = AeoAnalysisResult("coffee", "OpenAI", False)
    mock_sge.return_value = AeoAnalysisResult("coffee", "Google SGE", True, ["https://example.com/blog"])
    
    results = await analyze_aeo_visibility("example.com", "coffee")
    
    assert len(results) == 3
    assert results[0].ai_engine == "Perplexity"
    assert results[0].is_cited is True
    assert results[1].ai_engine == "OpenAI"
    assert results[1].is_cited is False
    assert results[2].ai_engine == "Google SGE"
    assert results[2].is_cited is True

@pytest.mark.asyncio
async def test_analyze_aeo_visibility_no_keys(mock_no_keys):
    results = await analyze_aeo_visibility("example.com", "coffee")
    
    assert len(results) == 1
    assert results[0].ai_engine == "None"
    assert "No AI Search API" in results[0].error

def test_format_aeo_report():
    results = [
        AeoAnalysisResult("test", "Perplexity", True, ["https://example.com/1"], "Keep it up"),
        AeoAnalysisResult("test", "Google SGE", False, [], "Format better")
    ]
    report = format_aeo_report("example.com", "test", results)
    
    assert "AI Citation & AEO Report" in report
    assert "Perplexity" in report
    assert "✅ CITED" in report
    assert "https://example.com/1" in report
    assert "Google SGE" in report
    assert "❌ NOT CITED" in report
