"""
Media SEO Module (Video & Voice).
Handles parsing and validating VideoObject and Speakable Schema (JSON-LD) for rich snippets and voice search.
"""

from crawler import crawl_page, extract_schema_data
from models import VideoSchemaResult, SpeakableSchemaResult, MediaSeoReport

async def analyze_media_seo(url: str) -> MediaSeoReport:
    """Analyzes a webpage's JSON-LD schema for Google Video Carousels and Assistant (Speakable)."""
    report = MediaSeoReport(url=url)
    try:
        html = await crawl_page(url)
    except Exception as e:
        report.error = f"Failed to crawl {url}: {str(e)}"
        return report

    schemas = extract_schema_data(html)
    video_schemas = []
    speakable_schema = None

    for schema in schemas:
        schema_type = schema.get("@type", "")
        
        # Handle single dictionary objects
        if schema_type == "VideoObject":
            video_schemas.append(schema)
        elif schema_type == "SpeakableSpecification" or "speakable" in schema:
            # Sometmes speakable is nested inside Article/NewsArticle
             speakable_schema = schema.get("speakable", schema) if "speakable" in schema else schema

        # Handle lists in @type
        elif isinstance(schema_type, list):
            if "VideoObject" in schema_type:
                video_schemas.append(schema)
            if "SpeakableSpecification" in schema_type:
               speakable_schema = schema

        # Look inside arrays if there's a @graph
        if "@graph" in schema and isinstance(schema["@graph"], list):
            for item in schema["@graph"]:
                item_type = item.get("@type", "")
                if item_type == "VideoObject" or (isinstance(item_type, list) and "VideoObject" in item_type):
                    video_schemas.append(item)
                elif item_type == "SpeakableSpecification" or (isinstance(item_type, list) and "SpeakableSpecification" in item_type) or "speakable" in item:
                    speakable_schema = item.get("speakable", item) if "speakable" in item else item

    # --- Video Analysis ---
    if not video_schemas:
        report.video_status = "Missing"
    else:
        incomplete_videos = 0
        for v_schema in video_schemas:
            v_result = VideoSchemaResult()
            v_missing = []

            v_result.name = v_schema.get("name", "")
            if not v_result.name: v_missing.append("name")

            v_result.description = v_schema.get("description", "")
            if not v_result.description: v_missing.append("description")

            v_result.upload_date = v_schema.get("uploadDate", "")
            if not v_result.upload_date: v_missing.append("uploadDate")

            v_result.thumbnail_url = v_schema.get("thumbnailUrl", "")
            if not v_result.thumbnail_url: v_missing.append("thumbnailUrl")

            v_result.content_url = v_schema.get("contentUrl", "")
            v_result.embed_url = v_schema.get("embedUrl", "")
            if not v_result.content_url and not v_result.embed_url:
                v_missing.append("contentUrl OR embedUrl")

            v_result.duration = v_schema.get("duration", "")
            if not v_result.duration: v_missing.append("duration") # recommended, not strictly required but good for SEO

            v_result.missing_fields = v_missing
            report.video_details.append(v_result)
            
            if v_missing:
                incomplete_videos += 1

        if incomplete_videos > 0:
            report.video_status = "Incomplete"
        else:
            report.video_status = "Valid"

    # --- Speakable Analysis ---
    s_result = SpeakableSchemaResult()
    if speakable_schema:
        s_result.is_present = True
        s_missing = []
        
        selectors = speakable_schema.get("cssSelector", [])
        if isinstance(selectors, str): selectors = [selectors]
        s_result.css_selectors = selectors
        
        xpaths = speakable_schema.get("xpath", [])
        if isinstance(xpaths, str): xpaths = [xpaths]
        s_result.xpath = xpaths
        
        if not s_result.css_selectors and not s_result.xpath:
             s_missing.append("cssSelector OR xpath")
             
        s_result.missing_fields = s_missing
        report.speakable_details = s_result
        
        if s_missing:
             report.speakable_status = "Incomplete"
        else:
             report.speakable_status = "Valid"
    else:
        report.speakable_status = "Missing"

    # --- Recommendations Generating ---
    recs = []
    if report.video_status == "Missing":
        recs.append("No VideoObject schema found. If you have videos on this page, add JSON-LD Video schema to be eligible for Google Video Carousels.")
    elif report.video_status == "Incomplete":
        recs.append(f"Found {len(report.video_details)} videos, but some are missing required fields (like thumbnailUrl, uploadDate, or contentUrl). Fix these to ensure Google indexes them properly.")
    else:
        recs.append("VideoObject schema is valid!")

    if report.speakable_status == "Missing":
        recs.append("No Speakable schema found. For news articles or informational blogs, adding this allows Google Assistant to read your content aloud.")
    elif report.speakable_status == "Incomplete":
        recs.append("Speakable schema found, but it lacks specific cssSelector or xpath targeting. You must tell Google exactly which text to read.")
    else:
         recs.append("Speakable schema is valid and ready for voice search!")
         
    report.recommendations = " ".join(recs)
    return report

def format_media_report(report: MediaSeoReport) -> str:
    """Format the Media SEO report for Claude."""
    if report.error:
        return f"⚠️ **Media SEO Error:** {report.error}"

    lines = [
        f"## 🎬 Media (Video & Voice) SEO Analysis",
        f"**URL:** `{report.url}`\n",
    ]
    
    # Video Section
    v_icon = "❌" if report.video_status == "Missing" else "⚠️" if report.video_status == "Incomplete" else "✅"
    lines.append(f"### Video SEO")
    lines.append(f"**Schema Status:** {v_icon} {report.video_status}")
    
    if report.video_details:
        lines.append(f"Found **{len(report.video_details)}** VideoObject(s):")
        for idx, v in enumerate(report.video_details, 1):
            name = v.name or "Unnamed Video"
            lines.append(f"\n**{idx}. {name}**")
            if v.thumbnail_url: lines.append(f"- Thumbnail: Yes")
            if v.upload_date: lines.append(f"- Uploaded: {v.upload_date}")
            if v.duration: lines.append(f"- Duration: {v.duration}")
            
            if v.missing_fields:
                lines.append(f"- **⚠️ Missing:** `{', '.join(v.missing_fields)}`")
                
    lines.append("\n---\n")
    
    # Voice Section
    s_icon = "❌" if report.speakable_status == "Missing" else "⚠️" if report.speakable_status == "Incomplete" else "✅"
    lines.append(f"### Voice Search SEO (Speakable)")
    lines.append(f"**Schema Status:** {s_icon} {report.speakable_status}")
    
    if report.speakable_status != "Missing":
         sd = report.speakable_details
         if sd.css_selectors: lines.append(f"- CSS Selectors target: `{', '.join(sd.css_selectors)}`")
         if sd.xpath: lines.append(f"- XPath target: `{', '.join(sd.xpath)}`")
         if sd.missing_fields: lines.append(f"- **⚠️ Missing:** `{', '.join(sd.missing_fields)}`")
         
    lines.append(f"\n**Recommendation:** {report.recommendations}")
    return "\n".join(lines)
