"""
Local SEO Module.
Handles Local Pack rankings, Geo tag generation, and Citation Building.
"""

import os
import httpx
from models import LocalRankingResult, GeoTag, CitationOpportunity, LocalSeoReport

async def analyze_local_rankings(business_name: str, keywords: list[str], location: str) -> LocalSeoReport:
    """Search SerpAPI for keywords using localized location parameter and check Local Pack presence."""
    api_key = os.environ.get("SERPAPI_KEY")
    report = LocalSeoReport(business_name=business_name, target_location=location)

    if not api_key:
        report.error = "SERPAPI_KEY is required for Local SEO tracking."
        return report

    if not keywords:
        report.error = "No keywords provided."
        return report

    try:
        async with httpx.AsyncClient() as client:
            for keyword in keywords:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "engine": "google",
                        "q": keyword,
                        "location": location,
                        "api_key": api_key,
                        "gl": "us",
                        "hl": "en"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    local_results = data.get("local_results", [])
                    
                    found = False
                    # local_results is usually a list of up to 3 or 4 places
                    for idx, place in enumerate(local_results, 1):
                        title = place.get("title", "")
                        if business_name.lower() in title.lower():
                            found = True
                            report.rankings.append(LocalRankingResult(
                                keyword=keyword,
                                location=location,
                                rank_in_local_pack=idx,
                                business_name=title,
                                rating=place.get("rating", 0.0),
                                reviews=place.get("reviews", 0)
                            ))
                            break
                    
                    if not found:
                         report.rankings.append(LocalRankingResult(
                                keyword=keyword,
                                location=location,
                                rank_in_local_pack=0, # 0 means not found
                                business_name=business_name,
                                error="Not found in Local 3-Pack"
                            ))
                else:
                    report.rankings.append(LocalRankingResult(
                        keyword=keyword,
                        location=location,
                        rank_in_local_pack=0,
                        business_name=business_name,
                        error=f"API Error: {response.status_code}"
                    ))
                    
        report.recommendations = _generate_local_recommendations(report.rankings)
        return report
    except Exception as e:
        report.error = f"Failed to run local search: {str(e)}"
        return report

def _generate_local_recommendations(rankings: list[LocalRankingResult]) -> str:
    """Generate recommendations based on local pack performance."""
    total = len(rankings)
    found = sum(1 for r in rankings if r.rank_in_local_pack > 0)
    
    if found == 0:
        return "You are missing from the Local Pack for these keywords. Ensure your Google Business Profile is verified, completely filled out, categories match your core keywords, and you are building local citations."
    elif found == total:
        return "Great visibility! You appear in the Local Pack for all checked keywords. Keep collecting positive reviews consistently to defend your rankings."
    else:
        return f"Appearing in {found}/{total} local packs. To break into the remaining packs, increase your review velocity and ensure your business name, address, and phone number (NAP) are consistent across local directory citations."

def generate_geo_tags(latitude: str, longitude: str, region: str, placename: str) -> GeoTag:
    """Generate geographical meta tags for HTML head."""
    tags = f"""<meta name="geo.region" content="{region}" />
<meta name="geo.placename" content="{placename}" />
<meta name="geo.position" content="{latitude};{longitude}" />
<meta name="ICBM" content="{latitude}, {longitude}" />"""
    
    return GeoTag(latitude, longitude, region, placename, tags)

def generate_citation_list(business_category: str, name: str, address: str, phone: str) -> list[CitationOpportunity]:
    """Generates a list of top citations to build with consistent NAP details."""
    citations = []
    
    nap_block = f"{name}\n{address}\n{phone}"
    
    # Core directories everyone needs
    core = [
        ("Google Business Profile", "google.com/business", 100),
        ("Bing Places", "bingplaces.com", 90),
        ("Apple Maps", "register.apple.com/placesonmaps", 90),
        ("Yelp", "yelp.com", 85),
        ("Foursquare", "foursquare.com", 80),
        ("Better Business Bureau", "bbb.org", 85)
    ]
    
    for c_name, domain, auth in core:
        citations.append(CitationOpportunity(
            directory_name=c_name,
            domain=domain,
            authority_score=auth,
            category="General",
            recommended_nap=nap_block
        ))
        
    cat_lower = business_category.lower()
    if "restaurant" in cat_lower or "food" in cat_lower or "cafe" in cat_lower:
        citations.append(CitationOpportunity("TripAdvisor", "tripadvisor.com", 90, "Food & Travel", nap_block))
        citations.append(CitationOpportunity("Zomato", "zomato.com", 80, "Food", nap_block))
    elif "law" in cat_lower or "attorney" in cat_lower:
        citations.append(CitationOpportunity("Avvo", "avvo.com", 80, "Legal", nap_block))
        citations.append(CitationOpportunity("FindLaw", "findlaw.com", 85, "Legal", nap_block))
    elif "health" in cat_lower or "doctor" in cat_lower or "dentist" in cat_lower:
        citations.append(CitationOpportunity("Healthgrades", "healthgrades.com", 80, "Healthcare", nap_block))
        citations.append(CitationOpportunity("Zocdoc", "zocdoc.com", 80, "Healthcare", nap_block))
        
    return citations

def format_local_seo_report(report: LocalSeoReport) -> str:
    """Format local rankings for Claude."""
    if report.error:
        return f"⚠️ **Local SEO Error:** {report.error}"
        
    lines = [
        f"## 📍 Local SEO Rankings",
        f"**Business:** `{report.business_name}`",
        f"**Location Context:** `{report.target_location}`",
        ""
    ]
    
    for r in report.rankings:
        if r.error and not "Not found" in r.error:
             lines.append(f"❌ **{r.keyword}:** API Error - {r.error}")
             continue
             
        if r.rank_in_local_pack > 0:
            lines.append(f"✅ **{r.keyword}:** Rank #{r.rank_in_local_pack} in Local Pack (⭐ {r.rating}, {r.reviews} reviews)")
        else:
            lines.append(f"❌ **{r.keyword}:** Not found in Local 3-Pack")
            
    lines.append(f"\n**Recommendation:** {report.recommendations}")
    return "\n".join(lines)

def format_geo_tags(geo: GeoTag) -> str:
    return f"## 🌍 Geo Meta Tags\nCopy and paste these directly into the `<head>` of your website to help search engines understand your physical location.\n\n```html\n{geo.html_tags}\n```"

def format_citations(citations: list[CitationOpportunity]) -> str:
    lines = [
        "## 🏢 Local Citation Building Plan",
        "Build profiles on these directories using the EXACT NAP (Name, Address, Phone) format below to ensure consistent local signals.",
        f"\n**Target NAP Block:**\n```\n{citations[0].recommended_nap}\n```\n",
        "| Directory | Domain | Authority | Category |",
        "|-----------|--------|-----------|----------|"
    ]
    for c in citations:
        lines.append(f"| {c.directory_name} | {c.domain} | {c.authority_score} | {c.category} |")
        
    return "\n".join(lines)
