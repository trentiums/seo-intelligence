# SEO Intelligence — Claude Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> AI-powered SEO toolkit built into Claude. Audit pages, analyze competitors, generate ranking plans, build schema markup, cluster keywords, and track AI search visibility.

## Install

In Claude Code:
```
/plugin install seo-intelligence
```

Or browse: `/plugin` → Discover → search **"seo-intelligence"**

---

## Skills (Auto-Activating)

Claude automatically uses these skills based on context — no commands needed.

| Skill | Triggers when you ask about... |
|-------|-------------------------------|
| **on-page-seo** | SEO score, title tags, meta descriptions, heading structure |
| **technical-seo** | Crawlability, sitemap, robots.txt, SSL, redirects, canonicals |
| **competitor-analysis** | Why competitors rank higher, SERP gap analysis |
| **keyword-research** | Keyword clustering, search intent, difficulty, cannibalization |
| **content-strategy** | Content briefs, blog outlines, what to write for a keyword |
| **schema-markup** | JSON-LD, structured data, rich results, FAQ/Product schema |
| **local-seo** | Google Maps, Local 3-Pack, citations, NAP consistency |
| **aeo-visibility** | AI search citations (Perplexity, ChatGPT, Google SGE) |
| **ranking-plan** | How to rank higher, prioritized SEO action plans |
| **ecommerce-seo** | Product page SEO, Google Merchant Center schema validation |
| **international-seo** | hreflang tags, multilingual sites, country targeting |

**Example prompts:**
```
"Why is my competitor ranking higher for 'best coffee maker'?"
"Check the SEO of https://mysite.com"
"What's the search intent for 'cold brew coffee recipe'?"
"Generate schema markup for my FAQ page at https://mysite.com/faq"
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `/seo-intelligence:seo-check <url> <keyword>` | Quick SEO health check — score + top 5 fixes |
| `/seo-intelligence:seo-audit <url> <keywords>` | Full multi-keyword audit with competitor analysis |
| `/seo-intelligence:technical-audit <url>` | Technical SEO infrastructure audit |
| `/seo-intelligence:competitor-gap <url> <keyword>` | Gap analysis against top 3 ranking pages |
| `/seo-intelligence:ranking-plan <url> <keyword>` | Prioritized action plan to rank higher |
| `/seo-intelligence:keyword-cluster <keywords>` | Cluster keywords + detect cannibalization |
| `/seo-intelligence:generate-schema <url> [type]` | Generate JSON-LD schema markup |
| `/seo-intelligence:content-brief <keyword>` | SEO content brief from competitor analysis |

---

## Agents

Three autonomous agents for multi-step SEO tasks:

### SEO Auditor
Runs a complete SEO audit autonomously — on-page analysis, technical check, competitor gap analysis, and prioritized action plan.
```
"Run an SEO audit on https://mysite.com for keywords: best coffee maker, coffee machine reviews"
```

### Competitor Analyzer
Researches top 5 SERP competitors, crawls each, and delivers a gap analysis showing exactly what they do better.
```
"Who is outranking me for 'best coffee maker' and why?"
```

### Content Strategist
Takes a keyword list and produces a complete content strategy — clustering, intent classification, content briefs, cannibalization fixes, and prioritized content calendar.
```
"Build a content strategy for: cold brew coffee, iced coffee, cold brew recipe, cold brew maker"
```

---

## MCP Tools (22 Tools)

All skills, agents, and commands are powered by these MCP tools:

| Tool | Description | API Key Required |
|------|-------------|-----------------|
| `analyze_page_seo` | Full on-page SEO health check | No |
| `search_serp` | Live Google SERP results | SerpAPI |
| `compare_with_competitors` | Competitor gap analysis | SerpAPI |
| `generate_ranking_plan` | Prioritized ranking action plan | SerpAPI |
| `get_quick_wins` | Top 5 easiest high-impact fixes | No |
| `technical_seo_audit` | Sitemap, robots.txt, SSL, redirects | No |
| `classify_search_intent` | Intent classification per keyword | SerpAPI |
| `cluster_keywords` | Group keywords by SERP URL overlap | SerpAPI |
| `detect_cannibalization` | Find competing pages for same keywords | SerpAPI |
| `predict_keyword_difficulty` | Ranking difficulty + ROI projection | SerpAPI |
| `check_ai_search_visibility` | AEO: Perplexity, ChatGPT, SGE citations | Optional |
| `analyze_entity` | Google Knowledge Graph entity validation | Optional |
| `check_local_pack` | Google Local 3-Pack presence check | SerpAPI |
| `build_local_citations` | Directory citation list by category | No |
| `generate_geo_tags` | HTML geo meta tags for local SEO | No |
| `ecommerce_product_seo` | Product schema + Merchant Center validation | No |
| `analyze_accessibility` | WCAG 2.1 AA + UX audit | No |
| `analyze_media_seo` | VideoObject + Speakable schema | No |
| `international_seo` | hreflang + HTML lang validation | No |

---

## API Keys

**SerpAPI** (free tier: 100 searches/month) powers all live SERP features.
Sign up: [serpapi.com](https://serpapi.com/users/sign_up?source=seo-intelligence)

10+ tools work with **zero API keys** — on-page analysis, technical audits, schema generation, local citations, accessibility, schema validation, and more work immediately after install.

Configure keys after installing the plugin: `/plugin config seo-intelligence`

---

## Architecture

Built with a BYOK (Bring Your Own Key) model — the plugin is free. You supply only the API keys you need for the features you use.

```
seo-intelligence/
├── .claude-plugin/plugin.json   # Plugin manifest
├── skills/                      # 11 auto-activating skills
├── agents/                      # 3 autonomous agents
├── commands/                    # 8 slash commands
├── server.py                    # MCP server entry point
├── crawler.py                   # Page crawling & HTML parsing
├── serp.py                      # SerpAPI integration
├── analyzer.py                  # Gap analysis, scoring, plans
├── technical.py                 # Technical SEO audits
├── content.py                   # Content briefs, clustering
├── ai_search.py                 # AEO visibility checks
├── entity.py                    # Knowledge Graph entity validation
├── predictive.py                # Difficulty & ROI prediction
├── local_seo.py                 # Local SEO & 3-Pack
├── ecommerce_seo.py             # Product schema validation
├── accessibility_seo.py         # WCAG 2.1 AA audits
├── media_seo.py                 # Video & voice schema
├── international_seo.py         # hreflang validation
└── tests/                       # 142+ pytest tests
```

---

## License

MIT — [Bhargav Patel](https://github.com/trentiums)
