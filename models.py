"""Data models for the SEO Intelligence plugin."""

from dataclasses import dataclass, field


@dataclass
class HeadingInfo:
    """Represents a heading found on a page."""
    level: int  # 1-6
    text: str


@dataclass
class LinkInfo:
    """Represents a link found on a page."""
    url: str
    text: str
    is_internal: bool


@dataclass
class ImageInfo:
    """Represents an image found on a page."""
    src: str
    alt: str
    has_alt: bool


@dataclass
class FAQItem:
    """Represents a FAQ question/answer pair."""
    question: str
    answer: str


@dataclass
class PageAnalysis:
    """Complete on-page analysis of a URL."""
    url: str
    title: str = ""
    meta_description: str = ""
    canonical_url: str = ""

    # Headings
    headings: list[HeadingInfo] = field(default_factory=list)
    h1_count: int = 0
    h2_count: int = 0
    h3_count: int = 0

    # Content
    word_count: int = 0
    content_text: str = ""

    # Links
    internal_links: list[LinkInfo] = field(default_factory=list)
    external_links: list[LinkInfo] = field(default_factory=list)
    internal_link_count: int = 0
    external_link_count: int = 0

    # Images
    images: list[ImageInfo] = field(default_factory=list)
    total_images: int = 0
    images_with_alt: int = 0
    images_without_alt: int = 0
    image_alt_coverage: float = 0.0

    # FAQ
    faqs: list[FAQItem] = field(default_factory=list)
    has_faq_section: bool = False

    # Schema / Structured Data
    schema_types: list[str] = field(default_factory=list)
    has_schema: bool = False

    # Open Graph
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    has_og_tags: bool = False

    # Technical
    has_viewport_meta: bool = False
    has_lang_attribute: bool = False
    has_charset: bool = False

    # Error
    error: str = ""


@dataclass
class SerpFeature:
    """SERP feature present for a keyword."""
    type: str  # e.g., "featured_snippet", "people_also_ask", "knowledge_panel"
    description: str = ""


@dataclass
class SerpResult:
    """A single organic result from SERP."""
    position: int
    title: str
    url: str
    snippet: str = ""
    displayed_url: str = ""


@dataclass
class SerpResponse:
    """Full SERP response for a keyword."""
    keyword: str
    organic_results: list[SerpResult] = field(default_factory=list)
    serp_features: list[SerpFeature] = field(default_factory=list)
    people_also_ask: list[str] = field(default_factory=list)
    total_results: int = 0
    error: str = ""


@dataclass
class GapDimension:
    """A single dimension in the gap analysis."""
    dimension: str  # e.g., "word_count", "headings", "meta_description"
    user_value: str
    competitor_avg: str
    gap: str
    recommendation: str
    severity: str = "medium"  # low, medium, high


@dataclass
class GapReport:
    """Complete gap analysis between user page and competitors."""
    user_url: str
    keyword: str
    competitor_urls: list[str] = field(default_factory=list)
    gaps: list[GapDimension] = field(default_factory=list)
    user_score: int = 0
    competitor_avg_score: int = 0
    summary: str = ""


@dataclass
class ActionItem:
    """A single action item in a ranking plan."""
    priority: int  # 1 = highest
    description: str
    category: str  # "content", "meta", "structure", "schema", "technical"
    effort: str  # "Easy", "Medium", "Hard"
    impact: str  # "High", "Medium", "Low"
    details: str = ""


@dataclass
class RankingPlan:
    """A complete ranking plan for a keyword."""
    url: str
    keyword: str
    current_issues: list[str] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    estimated_score_after: int = 0
    summary: str = ""


@dataclass
class SeoScore:
    """Overall SEO score breakdown."""
    overall: int = 0  # 0-100
    title_score: int = 0
    meta_score: int = 0
    headings_score: int = 0
    content_score: int = 0
    links_score: int = 0
    images_score: int = 0
    schema_score: int = 0
    technical_score: int = 0
    breakdown: dict[str, int] = field(default_factory=dict)


# ─── Phase 2 Models ─────────────────────────────────────────────────────────


@dataclass
class TechnicalCheckResult:
    """Result of a single technical SEO check."""
    check: str  # e.g., "sitemap", "robots_txt", "ssl"
    status: str  # "pass", "warn", "fail"
    details: str = ""
    recommendation: str = ""


@dataclass
class TechnicalAuditResult:
    """Complete technical SEO audit for a URL."""
    url: str
    checks: list[TechnicalCheckResult] = field(default_factory=list)
    passed: int = 0
    warnings: int = 0
    failed: int = 0
    overall_status: str = ""  # "Healthy", "Needs Attention", "Critical"
    error: str = ""


@dataclass
class SearchIntentResult:
    """Search intent classification for a keyword."""
    keyword: str
    intent: str  # "informational", "navigational", "transactional", "commercial"
    confidence: int = 0  # 0-100
    reasoning: str = ""
    recommended_content_type: str = ""  # "blog post", "product page", "landing page", etc.
    serp_signals: list[str] = field(default_factory=list)


@dataclass
class ContentBrief:
    """Auto-generated content brief for a keyword."""
    keyword: str
    suggested_title: str = ""
    target_word_count: int = 0
    suggested_headings: list[str] = field(default_factory=list)  # H2/H3 suggestions
    questions_to_answer: list[str] = field(default_factory=list)
    key_topics: list[str] = field(default_factory=list)
    competitor_urls: list[str] = field(default_factory=list)
    competitor_avg_word_count: int = 0
    search_intent: str = ""
    error: str = ""


@dataclass
class KeywordCluster:
    """A group of related keywords that can target a single page."""
    cluster_name: str
    primary_keyword: str
    related_keywords: list[str] = field(default_factory=list)
    shared_urls: list[str] = field(default_factory=list)  # URLs that rank for multiple keywords in cluster
    recommended_page_type: str = ""  # "pillar page", "blog post", etc.


@dataclass
class CannibalizationIssue:
    """A keyword cannibalization issue where multiple pages compete."""
    keyword: str
    conflicting_urls: list[str] = field(default_factory=list)
    severity: str = "medium"  # "low", "medium", "high"
    recommendation: str = ""


# ─── Phase 3 Models ─────────────────────────────────────────────────────────

@dataclass
class AeoAnalysisResult:
    """AEO visibility tracking for a keyword across AI engines."""
    keyword: str
    ai_engine: str  # "perplexity", "openai", "sge"
    is_cited: bool
    cited_urls: list[str] = field(default_factory=list)
    recommendations: str = ""
    error: str = ""

@dataclass
class EntityAnalysisResult:
    """Knowledge Graph entity verification."""
    entity_name: str
    description: str = ""
    kg_mid: str = ""  # Knowledge Graph ID
    wikipedia_url: str = ""
    confidence_score: float = 0.0
    recommendations: str = ""
    error: str = ""

@dataclass
class PredictiveScoring:
    """Keyword difficulty and traffic estimation."""
    keyword: str
    difficulty_score: int = 0  # 0-100
    estimated_traffic: int = 0
    error: str = ""


# ─── Phase 4 Models ─────────────────────────────────────────────────────────

@dataclass
class LocalRankingResult:
    """Local pack ranking result."""
    keyword: str
    location: str
    rank_in_local_pack: int  # 1, 2, 3, or None if not found
    business_name: str
    rating: float = 0.0
    reviews: int = 0
    error: str = ""

@dataclass
class GeoTag:
    """Generated Geo Meta Tags."""
    latitude: str
    longitude: str
    region: str
    placename: str
    html_tags: str = ""

@dataclass
class CitationOpportunity:
    """A directory citation to build."""
    directory_name: str
    domain: str
    authority_score: int
    category: str
    recommended_nap: str = ""

@dataclass
class LocalSeoReport:
    """Comprehensive local SEO report."""
    business_name: str
    target_location: str
    rankings: list[LocalRankingResult] = field(default_factory=list)
    recommendations: str = ""
    error: str = ""

@dataclass
class ProductSchemaResult:
    """Product JSON-LD schema analysis."""
    name: str = ""
    price: float = 0.0
    currency: str = ""
    availability: str = ""
    rating: float = 0.0
    review_count: int = 0
    missing_fields: list[str] = field(default_factory=list)

@dataclass
class EcommerceSeoReport:
    """Comprehensive e-commerce SEO report."""
    url: str
    product_name: str = ""
    schema_status: str = "Missing"  # "Valid", "Incomplete", "Missing"
    schema_details: ProductSchemaResult = field(default_factory=ProductSchemaResult)
    recommendations: str = ""
    error: str = ""

