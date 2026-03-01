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
