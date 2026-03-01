"""
Predictive Analytics Module for SEO Intelligence.
Calculates keyword difficulty and traffic estimations.
"""

from typing import Any
from models import PredictiveScoring

async def calculate_keyword_difficulty(keyword: str, serp_response: Any) -> PredictiveScoring:
    """
    Predicts SEO difficulty based on top 10 competitors in SERP.
    Difficulty (0-100) is calculated using heuristics:
    - Number of top 10 results with exact keyword match in title
    - Presence of high-authority domains (wikipedia, amazon, etc.)
    """
    if hasattr(serp_response, "error") and serp_response.error:
        return PredictiveScoring(
            keyword=keyword,
            error=f"Cannot calculate difficulty: SERP data error ({serp_response.error})"
        )
        
    results = getattr(serp_response, "organic_results", [])
    if not results:
        return PredictiveScoring(
            keyword=keyword,
            error="No organic results found to analyze difficulty."
        )

    score = 0
    kw_lower = keyword.lower()
    exact_title_matches = 0
    high_authority_domains = 0
    
    authority_markers = [
        "wikipedia.org", "amazon.", "youtube.com", "facebook.com", 
        "gov", "edu", "nytimes.com", "forbes.com", "apple.com", "webmd.com"
    ]
    
    total_analyzed = len(results)
    
    for res in results:
        # Check title match
        title = getattr(res, "title", "").lower()
        if kw_lower in title:
            exact_title_matches += 1
            
        # Check authority
        url = getattr(res, "url", "").lower()
        if any(marker in url for marker in authority_markers):
            high_authority_domains += 1
            
    # Base difficulty 20
    score = 20
    # Add points for every exact title match (max 40)
    score += (exact_title_matches / max(total_analyzed, 1)) * 40
    # Add points for every high authority domain (max 40)
    score += (high_authority_domains / max(total_analyzed, 1)) * 40
    
    # Cap at 100
    final_score = int(min(max(score, 1), 100))
    
    roi_msg = "Assuming 30% CTR for Position 1"
    if final_score >= 80:
        roi_msg += " (Hard to attain, >12 months effort)"
    elif final_score >= 50:
        roi_msg += " (Moderate effort, 6-12 months)"
    else:
        roi_msg += " (Accessible target, 3-6 months)"

    return PredictiveScoring(
        keyword=keyword,
        difficulty_score=final_score,
        estimated_traffic=0, 
        roi_projection=roi_msg
    )

def format_predictive_report(score: PredictiveScoring) -> str:
    """Format predictive scoring for Claude."""
    if score.error:
        return f"⚠️ **Predictive Analysis Failed:** {score.error}"
        
    lines = [
        f"## 📈 Predictive SEO Analysis",
        f"**Target Keyword:** `{score.keyword}`"
    ]
    
    diff = score.difficulty_score
    if diff >= 80:
        diff_label = "🔴 Hard"
    elif diff >= 50:
        diff_label = "🟡 Medium"
    else:
        diff_label = "🟢 Easy"
        
    lines.append(f"**Difficulty Score:** {diff}/100 ({diff_label})")
    lines.append(f"**ROI & Timeline Projection:** {score.roi_projection}")
    lines.append("\n> *Note: Difficulty is estimated based on SERP title optimization and domain authority presence in the top organic results.*")
    
    return "\n".join(lines)
