"""
AI Search Engine visibility tracking and Answer Engine Optimization (AEO).
Supports Perplexity, OpenAI, and SerpAPI (for Google SGE).
"""

import os
import httpx
from urllib.parse import urlparse
from models import AeoAnalysisResult

async def analyze_aeo_visibility(domain: str, keyword: str) -> list[AeoAnalysisResult]:
    """
    Checks if a domain is cited in AI search engines for a given keyword.
    Uses available API keys to query Perplexity, OpenAI, and/or SerpAPI.
    """
    results = []
    
    # Check Perplexity
    perplexity_key = os.environ.get("PERPLEXITY_API_KEY")
    if perplexity_key:
        result = await _check_perplexity(domain, keyword, perplexity_key)
        results.append(result)
        
    # Check OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        result = await _check_openai(domain, keyword, openai_key)
        results.append(result)
        
    # Check Google SGE via SerpAPI
    serpapi_key = os.environ.get("SERPAPI_KEY")
    if serpapi_key:
        result = await _check_sge(domain, keyword, serpapi_key)
        results.append(result)
        
    if not results:
        results.append(AeoAnalysisResult(
            keyword=keyword,
            ai_engine="None",
            is_cited=False,
            error="No AI Search API keys found. Please provide PERPLEXITY_API_KEY, OPENAI_API_KEY, or SERPAPI_KEY."
        ))
        
    return results

async def _check_perplexity(domain: str, keyword: str, api_key: str) -> AeoAnalysisResult:
    """Queries Perplexity API with sonar-pro to check citations."""
    try:
        async with httpx.AsyncClient() as client:
            # Note: Perplexity sonar models support online search
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {"role": "system", "content": "You are a helpful search assistant. Provide a comprehensive answer. Always cite your sources with URLs."},
                        {"role": "user", "content": keyword}
                    ],
                    "return_citations": True
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                citations = data.get("citations", [])
                
                # Check if domain is in any citation
                is_cited = False
                cited_urls = []
                cleaned_domain = urlparse(domain).netloc if domain.startswith("http") else domain
                
                for citation in citations:
                    if cleaned_domain in citation:
                        is_cited = True
                        cited_urls.append(citation)
                        
                recommendations = _generate_aeo_recommendations(is_cited, "Perplexity")
                
                return AeoAnalysisResult(
                    keyword=keyword,
                    ai_engine="Perplexity (sonar-pro)",
                    is_cited=is_cited,
                    cited_urls=cited_urls,
                    recommendations=recommendations
                )
            else:
                return AeoAnalysisResult(keyword=keyword, ai_engine="Perplexity", is_cited=False, error=f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        return AeoAnalysisResult(keyword=keyword, ai_engine="Perplexity", is_cited=False, error=str(e))

async def _check_openai(domain: str, keyword: str, api_key: str) -> AeoAnalysisResult:
    """Queries OpenAI API (uses o3-mini/gpt-4o hypothetically if we want web browsing, or evaluates AEO).
       Since standard chat completions don't reliably return live URLs without explicit search tools,
       we will prompt it to evaluate the query from an AEO perspective and see what it knows about the domain.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": "You are an AI providing authoritative answers. When answering, list the top 3 URLs you would cite for this topic."},
                        {"role": "user", "content": f"Topic: {keyword}\n\nProvide an answer and list 3 source URLs. Do the sources you think of include {domain}?"}
                    ],
                    "temperature": 0.2
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                cleaned_domain = urlparse(domain).netloc if domain.startswith("http") else domain
                is_cited = cleaned_domain.lower() in content.lower()
                
                recommendations = _generate_aeo_recommendations(is_cited, "OpenAI / ChatGPT")
                
                return AeoAnalysisResult(
                    keyword=keyword,
                    ai_engine="OpenAI (gpt-4o)",
                    is_cited=is_cited,
                    cited_urls=[], # Difficult to reliably extract list, so we leave empty
                    recommendations=recommendations
                )
            else:
                return AeoAnalysisResult(keyword=keyword, ai_engine="OpenAI", is_cited=False, error=f"API Error {response.status_code}: {response.text}")
                
    except Exception as e:
        return AeoAnalysisResult(keyword=keyword, ai_engine="OpenAI", is_cited=False, error=str(e))

async def _check_sge(domain: str, keyword: str, api_key: str) -> AeoAnalysisResult:
    """Queries SerpAPI to extract citations from Google's AI Overview (SGE)."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google",
                    "q": keyword,
                    "api_key": api_key,
                    "gl": "us",
                    "hl": "en"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                ai_overview = data.get("ai_overview", {})
                if not ai_overview:
                    return AeoAnalysisResult(keyword=keyword, ai_engine="Google SGE", is_cited=False, error="No AI Overview triggered for this query.")
                
                citations = ai_overview.get("organic_results", []) # Use organic_results as stand in if explicit SGE sources aren't structured well, actually we should look closely at SerpAPI dict
                
                # We will check if "ai_overview" contains links if available 
                # According to SerpAPI SGE doc, it's a string, or dict, usually text.
                is_cited = False
                cited_urls = []
                cleaned_domain = urlparse(domain).netloc if domain.startswith("http") else domain
                
                # Check within the text of the AI overview if specific sources are not parsed out
                overview_text = str(ai_overview).lower()
                if cleaned_domain.lower() in overview_text:
                    is_cited = True
                    cited_urls.append("Found in Google AI Overview text")
                        
                recommendations = _generate_aeo_recommendations(is_cited, "Google SGE")
                
                return AeoAnalysisResult(
                    keyword=keyword,
                    ai_engine="Google SGE",
                    is_cited=is_cited,
                    cited_urls=cited_urls,
                    recommendations=recommendations
                )
            else:
                return AeoAnalysisResult(keyword=keyword, ai_engine="Google SGE", is_cited=False, error=f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        return AeoAnalysisResult(keyword=keyword, ai_engine="Google SGE", is_cited=False, error=str(e))


def _generate_aeo_recommendations(is_cited: bool, engine: str) -> str:
    """Returns general recommendations for Answer Engine Optimization based on citation status."""
    if is_cited:
        return f"✅ Strong visibility! You are cited by {engine}. Maintain authority by keeping content fresh, factual, and well-structured (lists, tables)."
    else:
        return f"❌ Not cited by {engine}. To improve AEO: \n1. Formulate direct, concise answers (TL;DR paragraphs) at the top of content.\n2. Use structured HTML (<ul>, <table>, <dl>).\n3. Earn authoritative backlinks so AI models trust your domain as a primary source."


def format_aeo_report(domain: str, keyword: str, results: list[AeoAnalysisResult]) -> str:
    """Formats the AEO visibility results for Claude."""
    lines = [
        f"## 🤖 AI Citation & AEO Report",
        f"**Domain:** `{domain}`",
        f"**Keyword:** `{keyword}`\n"
    ]
    
    for res in results:
        lines.append(f"### Engine: {res.ai_engine}")
        if res.error:
            lines.append(f"⚠️ **Status:** Skipped or Failed ({res.error})")
        else:
            status = "✅ CITED" if res.is_cited else "❌ NOT CITED"
            lines.append(f"**Visibility:** {status}")
            
            if res.cited_urls:
                lines.append("**Cited URLs:**")
                for url in res.cited_urls:
                    lines.append(f"- {url}")
                    
            lines.append(f"\n**Recommendation:** {res.recommendations}")
        lines.append("\n---")
        
    lines.append("\n> **AEO Tip:** AI engines prefer factual density, direct answers (position zero targets), and high-authority contextual links.")
    return "\n".join(lines)
