"""
Entity SEO & Knowledge Graph tools.
Interfaces with Google Knowledge Graph Search API.
"""

import os
import httpx
from models import EntityAnalysisResult

async def verify_entity(keyword: str) -> list[EntityAnalysisResult]:
    """
    Search for a keyword in the Google Knowledge Graph to identify official entities.
    Returns matched entities with their KG IDs (mids), descriptions, and Wikipedia links.
    """
    api_key = os.environ.get("GOOGLE_CLOUD_API_KEY")
    results = []
    
    if not api_key:
        results.append(EntityAnalysisResult(
            entity_name=keyword,
            error="GOOGLE_CLOUD_API_KEY is not configured. Entity verification requires access to the Google Knowledge Graph Search API."
        ))
        return results

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://kgsearch.googleapis.com/v1/entities:search",
                params={
                    "query": keyword,
                    "key": api_key,
                    "limit": 3,
                    "indent": True
                },
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get("itemListElement", [])
                
                if not items:
                    results.append(EntityAnalysisResult(
                        entity_name=keyword,
                        error="No Knowledge Graph entities found for this keyword."
                    ))
                    return results

                for item in items:
                    result_node = item.get("result", {})
                    score = item.get("resultScore", 0.0)
                    
                    name = result_node.get("name", keyword)
                    description = result_node.get("detailedDescription", {}).get("articleBody", "")
                    if not description:
                        description = result_node.get("description", "")
                        
                    kg_id = result_node.get("@id", "")
                    if kg_id.startswith("kg:"):
                        kg_mid = kg_id[3:]
                    else:
                        kg_mid = kg_id
                        
                    wikipedia_url = result_node.get("detailedDescription", {}).get("url", "")
                    
                    recommendations = _generate_entity_recommendations(kg_mid, wikipedia_url)

                    results.append(EntityAnalysisResult(
                        entity_name=name,
                        description=description,
                        kg_mid=kg_mid,
                        wikipedia_url=wikipedia_url,
                        confidence_score=score,
                        recommendations=recommendations
                    ))
                return results

            else:
                results.append(EntityAnalysisResult(
                    entity_name=keyword,
                    error=f"Knowledge Graph API Error {response.status_code}: {response.text}"
                ))
                return results

    except Exception as e:
        results.append(EntityAnalysisResult(
            entity_name=keyword,
            error=f"Failed to query Knowledge Graph: {str(e)}"
        ))
        return results

def _generate_entity_recommendations(kg_mid: str, wikipedia_url: str) -> str:
    """Generate schema markup recommendations for a verified entity."""
    recs = [
        "Strengthen this entity association on your pages using JSON-LD schema markup."
    ]
    if kg_mid:
        recs.append(f'Add `"@id": "kg:{kg_mid}"` to your Organization, Person, or About schema.')
    if wikipedia_url:
        recs.append(f'Add `"sameAs": "{wikipedia_url}"` to establish authority.')
    
    return " ".join(recs)

def format_entity_report(keyword: str, results: list[EntityAnalysisResult]) -> str:
    """Format Knowledge Graph search results for Claude."""
    lines = [
        f"## 🏛️ Entity SEO & Knowledge Graph Analysis",
        f"**Target Keyword:** `{keyword}`\n"
    ]

    for i, res in enumerate(results, 1):
        if res.error:
            lines.append(f"⚠️ **Status:** Skipped or Failed ({res.error})")
        else:
            lines.extend([
                f"### {i}. Entity: {res.entity_name} (Score: {res.confidence_score})",
                f"**Description:** {res.description}",
                f"**Knowledge Graph ID (MID):** `{res.kg_mid}`",
                f"**Wikipedia:** {res.wikipedia_url if res.wikipedia_url else 'None'}",
                f"\n**Recommendation:** {res.recommendations}"
            ])
        lines.append("\n---")
    
    lines.append("\n> **Entity SEO Tip:** Using official Knowledge Graph IDs (`@id`) helps search engines disambiguate concepts and build topical authority.")
    return "\n".join(lines)
