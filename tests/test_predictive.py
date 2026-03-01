import pytest
from models import PredictiveScoring
from predictive import calculate_keyword_difficulty, format_predictive_report
from serp import SerpResponse, SerpResult

@pytest.mark.asyncio
async def test_calculate_keyword_difficulty_hard():
    # Construct a fake SERP response with high authority and exact matches
    results = [
        SerpResult(1, "Best coffee maker", "https://amazon.com/coffee", "snippet"),
        SerpResult(2, "Best Coffee Maker 2026", "https://nytimes.com/coffee", "snippet"),
        SerpResult(3, "Coffee Maker Reviews", "https://wikipedia.org/wiki/Coffee_maker", "snippet")
    ]
    response = SerpResponse("best coffee maker", organic_results=results)
    
    score = await calculate_keyword_difficulty("best coffee maker", response)
    
    assert score is not None
    assert score.difficulty_score > 80  # Should be hard due to exact matches and big domains
    assert "Hard to attain" in score.roi_projection

@pytest.mark.asyncio
async def test_calculate_keyword_difficulty_easy():
    # Construct a fake SERP response with low authority and no exact matches
    results = [
        SerpResult(1, "My blog post", "https://smallblog.com/post", "snippet"),
        SerpResult(2, "Another post", "https://randomsite.net/page", "snippet"),
        SerpResult(3, "Thoughts", "https://example.org/thoughts", "snippet")
    ]
    response = SerpResponse("obscure long tail keyword here", organic_results=results)
    
    score = await calculate_keyword_difficulty("obscure long tail keyword here", response)
    
    assert score is not None
    assert score.difficulty_score < 50
    assert "Accessible target" in score.roi_projection

def test_format_predictive_report():
    score = PredictiveScoring(keyword="test keyword", difficulty_score=85, estimated_traffic=0, roi_projection="Hard (12 months)")
    report = format_predictive_report(score)
    
    assert "Predictive SEO Analysis" in report
    assert "test keyword" in report
    assert "85/100" in report
    assert "🔴 Hard" in report
