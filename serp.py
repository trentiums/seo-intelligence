"""SerpAPI integration for keyword SERP data."""

import os

import httpx

from models import SerpResult, SerpResponse, SerpFeature


SERPAPI_BASE_URL = "https://serpapi.com/search.json"


async def search_keyword(
    keyword: str,
    api_key: str | None = None,
    num_results: int = 3,
    location: str | None = None,
    language: str = "en",
    country: str = "us",
) -> SerpResponse:
    """Search a keyword via SerpAPI and return structured results.

    Args:
        keyword: The search query.
        api_key: SerpAPI key. Falls back to SERPAPI_KEY env var.
        num_results: Number of organic results to return (default 3).
        location: Geographic location for results (e.g., "Austin, Texas").
        language: Language code (default "en").
        country: Country code for Google domain (default "us").

    Returns:
        A SerpResponse with organic results, SERP features, and PAA questions.
    """
    key = api_key or os.environ.get("SERPAPI_KEY", "")
    if not key:
        return SerpResponse(
            keyword=keyword,
            error="SERPAPI_KEY not set. Please configure your SerpAPI key.",
        )

    params = {
        "q": keyword,
        "api_key": key,
        "engine": "google",
        "num": min(num_results * 2, 20),  # Fetch extra in case of filtering
        "hl": language,
        "gl": country,
    }
    if location:
        params["location"] = location

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(SERPAPI_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        return SerpResponse(
            keyword=keyword,
            error=f"SerpAPI HTTP error: {e.response.status_code} — {e.response.text[:200]}",
        )
    except httpx.RequestError as e:
        return SerpResponse(
            keyword=keyword,
            error=f"SerpAPI request failed: {str(e)}",
        )

    return parse_serp_response(data, keyword, num_results)


def parse_serp_response(
    data: dict, keyword: str, num_results: int = 3
) -> SerpResponse:
    """Parse raw SerpAPI JSON into a SerpResponse.

    Args:
        data: Raw JSON dict from SerpAPI.
        keyword: The original keyword searched.
        num_results: Max number of organic results to include.

    Returns:
        Structured SerpResponse.
    """
    response = SerpResponse(keyword=keyword)

    # --- Organic Results ---
    organic = data.get("organic_results", [])
    for item in organic[:num_results]:
        result = SerpResult(
            position=item.get("position", 0),
            title=item.get("title", ""),
            url=item.get("link", ""),
            snippet=item.get("snippet", ""),
            displayed_url=item.get("displayed_link", ""),
        )
        response.organic_results.append(result)

    # --- Total results ---
    search_info = data.get("search_information", {})
    response.total_results = search_info.get("total_results", 0)

    # --- SERP Features ---
    response.serp_features = _extract_serp_features(data)

    # --- People Also Ask ---
    paa = data.get("related_questions", [])
    response.people_also_ask = [q.get("question", "") for q in paa if q.get("question")]

    return response


def _extract_serp_features(data: dict) -> list[SerpFeature]:
    """Detect which SERP features are present."""
    features = []

    if data.get("answer_box"):
        features.append(SerpFeature(
            type="featured_snippet",
            description="Featured snippet / answer box present",
        ))

    if data.get("knowledge_graph"):
        kg = data["knowledge_graph"]
        features.append(SerpFeature(
            type="knowledge_panel",
            description=f"Knowledge panel: {kg.get('title', 'Unknown')}",
        ))

    if data.get("related_questions"):
        features.append(SerpFeature(
            type="people_also_ask",
            description=f"{len(data['related_questions'])} PAA questions",
        ))

    if data.get("local_results"):
        features.append(SerpFeature(
            type="local_pack",
            description="Local pack / map results present",
        ))

    if data.get("top_stories"):
        features.append(SerpFeature(
            type="top_stories",
            description="Top stories carousel present",
        ))

    if data.get("inline_videos"):
        features.append(SerpFeature(
            type="video_carousel",
            description="Video carousel present",
        ))

    if data.get("inline_images"):
        features.append(SerpFeature(
            type="image_pack",
            description="Image pack present",
        ))

    if data.get("shopping_results"):
        features.append(SerpFeature(
            type="shopping_results",
            description="Shopping results present",
        ))

    return features


def format_serp_response(response: SerpResponse) -> str:
    """Format a SerpResponse into a readable string for Claude."""
    if response.error:
        return f"❌ SERP search error for '{response.keyword}': {response.error}"

    lines = [
        f"# SERP Results: \"{response.keyword}\"",
        f"*Total results: {response.total_results:,}*",
        "",
    ]

    # Organic results
    if response.organic_results:
        lines.append("## Top Organic Results")
        for r in response.organic_results:
            lines.extend([
                f"### #{r.position} — {r.title}",
                f"- **URL**: {r.url}",
                f"- **Snippet**: {r.snippet}",
                "",
            ])

    # SERP features
    if response.serp_features:
        lines.append("## SERP Features Present")
        for f in response.serp_features:
            lines.append(f"- **{f.type}**: {f.description}")
        lines.append("")

    # People Also Ask
    if response.people_also_ask:
        lines.append("## People Also Ask")
        for q in response.people_also_ask:
            lines.append(f"- {q}")
        lines.append("")

    return "\n".join(lines)
