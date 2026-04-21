# SEO Intelligence — Your AI-Powered SEO Analyst Inside Claude

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![BYOK](https://img.shields.io/badge/Model-BYOK-orange)](https://serpapi.com)

> Turn Claude into a full-stack SEO expert. Audit pages, analyze competitors, generate ranking plans, build schema markup, cluster keywords, and track AI search visibility — all through natural conversation.

**No dashboards. No learning curve. Just type.**

---

## What is SEO Intelligence?

SEO Intelligence is a Claude plugin that brings 20+ years of SEO expertise directly into your Claude conversations. It ships with **11 auto-activating skills**, **3 autonomous agents**, **8 slash commands**, and **22 MCP tools** — covering every aspect of modern SEO from on-page analysis to AI search visibility.

Install once. Claude handles the rest.

---

## Skills (Auto-Activating)

Skills activate automatically based on what you're asking — no commands needed. Claude detects SEO-related context and invokes the right skill.

### On-Page SEO
Crawls any URL for a full SEO health check: title, meta, headings, images, links, schema, Open Graph, and an overall SEO score (0–100).

**Triggers:** "check my SEO", "SEO score", "analyze this page", "what's wrong with my meta"

```
"Check the SEO of https://myblog.com/post"
"What's my SEO score for this URL?"
"Is my title tag optimized?"
```

---

### Technical SEO
Audits site infrastructure: sitemap.xml, robots.txt, SSL/HTTPS, redirect chains, canonical tags, mobile viewport, lang attribute.

**Triggers:** "technical SEO", "crawl issues", "sitemap", "robots.txt", "canonical tags", "indexing"

```
"Run a technical SEO audit on https://mysite.com"
"Is my site crawlable?"
"Check my robots.txt"
```

---

### Competitor Analysis
Finds top 3 organic competitors for a keyword, crawls each, and delivers a gap analysis comparing content depth, schema types, heading structure, and more.

**Triggers:** "why does X rank higher", "competitor analysis", "outrank", "gap analysis"

```
"Why is my competitor outranking me for 'best coffee maker'?"
"Compare my page against the top results for 'project management software'"
```

---

### Keyword Research
Clusters keywords by SERP URL overlap, classifies search intent, estimates difficulty, and detects cannibalization.

**Triggers:** "keyword clustering", "search intent", "keyword difficulty", "cannibalization"

```
"Cluster these keywords: cold brew coffee, iced coffee, cold brew recipe"
"What's the search intent for 'best coffee maker 2026'?"
"Check for keyword cannibalization across my site"
```

---

### Content Strategy
Generates data-driven content briefs from competitor analysis: title, meta, heading structure, word count, questions to answer, must-cover topics.

**Triggers:** "content brief", "blog post outline", "content plan", "what to write"

```
"Write a content brief for 'how to make cold brew coffee'"
"What should I include in an article about project management software?"
"Give me a content outline for 'best coffee maker'"
```

---

### Schema Markup
Generates and validates JSON-LD schema markup. Supports Article, Product, LocalBusiness, FAQ, VideoObject, Speakable, and BreadcrumbList.

**Triggers:** "schema markup", "structured data", "JSON-LD", "rich results", "rich snippets"

```
"Generate FAQ schema for https://mysite.com/faq"
"Why aren't my rich results showing in Google?"
"Add Product schema to my product page"
```

---

### Local SEO
Checks Google Local 3-Pack presence, builds citation opportunities list, generates geo meta tags, and creates LocalBusiness schema.

**Triggers:** "local SEO", "Google Maps", "Local Pack", "citations", "local business"

```
"Does my business appear in the Google 3-Pack for 'dentist near me' in Austin TX?"
"Build a citation list for my dental clinic"
"Generate geo meta tags for my business location"
```

---

### AEO Visibility
Checks if your domain is cited as a source in Perplexity, ChatGPT, and Google SGE for target queries.

**Triggers:** "AEO", "AI search", "Perplexity", "ChatGPT citations", "answer engine"

```
"Is my domain cited in Perplexity for 'best coffee maker'?"
"Check my AEO visibility for target queries"
"Am I appearing in AI search results?"
```

---

### Ranking Plan
Generates a prioritized action plan to rank higher: numbered steps with effort (Easy/Medium/Hard), impact (High/Medium/Low), category, and implementation time.

**Triggers:** "how to rank", "ranking plan", "improve ranking", "what to fix"

```
"How do I rank higher for 'best coffee maker'?"
"Give me an SEO action plan for https://mysite.com/coffee"
"What should I fix to improve my rankings?"
```

---

### E-Commerce SEO
Validates Product JSON-LD schema against Google Merchant Center requirements. Flags missing price, availability, ratings, and brand.

**Triggers:** "product page SEO", "ecommerce SEO", "product schema", "Google Merchant"

```
"Check the product SEO for https://mystore.com/products/matcha"
"Why isn't my product showing rich results in Google?"
"Validate my WooCommerce product schema"
```

---

### International SEO
Validates HTML `lang` attributes and `hreflang` tags for multilingual sites. Checks self-referencing, x-default, reciprocal tags, and canonical conflicts.

**Triggers:** "hreflang", "international SEO", "multilingual", "country targeting"

```
"Check my hreflang implementation on https://mystore.com/en-us"
"Is my international SEO set up correctly?"
"Validate my multilingual site's language tags"
```

---

## Commands

Type these slash commands for instant, targeted SEO actions:

### `/seo-intelligence:seo-check <url> <keyword>`
Quick SEO health check. Returns score, section-by-section analysis, and top 5 quick wins.
```
/seo-intelligence:seo-check https://myblog.com/post best coffee maker
```

### `/seo-intelligence:seo-audit <url> <keyword1>, <keyword2>, ...`
Full multi-keyword audit. Competitor analysis, gap analysis, and ranking plans per keyword. Overall site SEO score.
```
/seo-intelligence:seo-audit https://mysite.com best coffee maker, coffee machine reviews
```

### `/seo-intelligence:technical-audit <url>`
Technical SEO infrastructure check. Pass/Warn/Fail for sitemap, robots.txt, SSL, redirects, canonicals, mobile.
```
/seo-intelligence:technical-audit https://mysite.com
```

### `/seo-intelligence:competitor-gap <url> <keyword>`
Gap analysis against top 3 SERP competitors. Comparison table + top gaps sorted by ranking impact.
```
/seo-intelligence:competitor-gap https://mysite.com/coffee best coffee maker
```

### `/seo-intelligence:ranking-plan <url> <keyword>`
Prioritized action plan sorted by highest impact + lowest effort. Includes timeline estimate.
```
/seo-intelligence:ranking-plan https://mysite.com/coffee best coffee maker
```

### `/seo-intelligence:keyword-cluster <keywords>`
Cluster keywords by SERP overlap. Detect cannibalization. Classify search intent per keyword.
```
/seo-intelligence:keyword-cluster cold brew coffee, iced coffee, cold brew recipe
```

### `/seo-intelligence:generate-schema <url> [type]`
Generate production-ready JSON-LD schema. Auto-detects type or specify: Article, Product, LocalBusiness, FAQ, VideoObject.
```
/seo-intelligence:generate-schema https://mysite.com/faq FAQ
```

### `/seo-intelligence:content-brief <keyword>`
SEO content brief from competitor analysis: title, meta, headings, word count, PAA questions, must-cover topics.
```
/seo-intelligence:content-brief how to make cold brew coffee
```

---

## Agents

Three autonomous agents handle complex, multi-step SEO tasks end-to-end.

### SEO Auditor
Runs a complete SEO audit autonomously — on-page analysis, technical check, SERP competitor research, gap analysis, and prioritized action plan. No step-by-step instructions needed.

**When to use:** Full site audits, client reports, pre-launch SEO checks

```
"Run an SEO audit on https://mysite.com for keywords: best coffee maker, coffee machine reviews"
"Audit my site at https://mysite.com"
"Full SEO report for https://mysite.com targeting coffee maker"
```

**What it delivers:**
- Overall SEO score (0–100)
- Technical health checklist (PASS/WARN/FAIL)
- On-page scores per section
- Competitor comparison table per keyword
- Prioritized action plan sorted by ROI
- Quick wins section

---

### Competitor Analyzer
Researches top 5 SERP competitors for a keyword, crawls each, and delivers a gap analysis showing exactly what they're doing better than you.

**When to use:** Understanding why you're not ranking, competitive research, market analysis

```
"Who is outranking me for 'best coffee maker' and why?"
"Analyze my competitors for 'project management software' vs https://myapp.com"
"What do the top results for 'cold brew coffee' have that I don't?"
```

**What it delivers:**
- Competitor profile table (5 competitors, key metrics)
- Your page vs. average competitor scores
- Gap list with opportunity scores
- Specific implementation instructions per gap

---

### Content Strategist
Takes a keyword list and produces a complete content strategy — clustering, intent classification, content briefs, cannibalization fixes, and a prioritized content calendar.

**When to use:** Planning content for a new site, building a content calendar, briefing a writing team

```
"Build a content strategy for: cold brew coffee, iced coffee, cold brew recipe, cold brew maker"
"Create content briefs for my coffee keyword list"
"Which of these keywords should I write about first?"
```

**What it delivers per keyword cluster:**
- Recommended target page (new or existing)
- Full content brief (title, meta, headings, word count, questions, topics)
- Schema type recommendation
- Estimated ranking difficulty + timeline

**Summary output:**
- Content calendar priority order
- Internal linking map between clusters
- Cannibalization fix recommendations

---

## Use Cases

### Blogger / Content Creator
> *"I just published a new post. Is my SEO good enough to rank?"*

```
"Check the SEO of https://myblog.com/best-coffee-brewing-methods and give me quick wins"
```

Claude crawls the post, returns an SEO score, section-by-section breakdown, and the 5 fastest fixes to improve rankings.

---

### Startup Founder
> *"How does our landing page stack up against competitors in search?"*

```
"Compare https://myapp.com/features against competitors for 'project management software'"
```

See exactly where your page falls short — content depth, schema, FAQ coverage, link profiles — and what to fix first.

---

### Freelance SEO Consultant
> *"I need to deliver a professional audit report to my client within the hour."*

```
"Run an SEO audit on https://clientsite.com for keywords: custom wedding cakes, wedding cake designs, best wedding bakery near me"
```

Complete structured audit report with per-keyword rankings, gap analyses, and prioritized action plans.

---

### E-Commerce Store Owner
> *"My product pages aren't showing in Google. What am I doing wrong?"*

```
/seo-intelligence:seo-check https://mystore.com/organic-matcha best organic matcha powder
```

Instant product page SEO score + schema validation against Google Merchant Center requirements.

---

### Content Strategist / Agency
> *"I need to plan 6 months of content for a client."*

```
"Build a content strategy for these 20 keywords: [list]"
```

The Content Strategist agent clusters keywords, classifies intent, identifies gaps, and delivers production-ready briefs — all in one run.

---

### Developer Building a Site
> *"I built the site but know nothing about SEO. Where do I start?"*

```
"Find quick SEO wins and run a technical audit for https://myportfolio.dev"
```

Immediate technical health check + 5 highest-impact fixes, no SEO expertise required.

---

### Local Business Owner
> *"Why isn't my business showing up in Google Maps?"*

```
"Analyze local SEO for my dental clinic 'Austin Smiles' in Austin TX for keyword 'dentist near me'"
```

3-Pack presence check, competitor list, citation opportunities, LocalBusiness schema, and geo meta tags.

---

## MCP Tools Reference (22 Tools)

All skills, agents, and commands are powered by these underlying MCP tools:

| Tool | Description | API Key |
|------|-------------|---------|
| `analyze_page_seo` | Full on-page SEO analysis | No |
| `search_serp` | Live Google SERP results | SerpAPI |
| `compare_with_competitors` | Competitor gap analysis | SerpAPI |
| `generate_ranking_plan` | Prioritized ranking action plan | SerpAPI |
| `get_quick_wins` | Top 5 easiest high-impact fixes | No |
| `technical_seo_audit` | Sitemap, robots.txt, SSL, redirects | No |
| `classify_search_intent` | Search intent classification | SerpAPI |
| `cluster_keywords` | Group keywords by SERP overlap | SerpAPI |
| `detect_cannibalization` | Find competing pages for same keywords | SerpAPI |
| `predict_keyword_difficulty` | Difficulty score + ROI projection | SerpAPI |
| `check_ai_search_visibility` | AEO: Perplexity, ChatGPT, SGE | Optional |
| `analyze_entity` | Google Knowledge Graph validation | Optional |
| `check_local_pack` | Google Local 3-Pack presence | SerpAPI |
| `build_local_citations` | Directory citation list by category | No |
| `generate_geo_tags` | HTML geo meta tags | No |
| `ecommerce_product_seo` | Product schema + Merchant Center | No |
| `analyze_accessibility` | WCAG 2.1 AA + UX audit | No |
| `analyze_media_seo` | VideoObject + Speakable schema | No |
| `international_seo` | hreflang + HTML lang validation | No |

---

## Pricing & API Keys

SEO Intelligence is **100% free and open source** (MIT). You provide API keys only for external data services you want to use.

| Service | Cost | Powers |
|---------|------|--------|
| SerpAPI | Free: 100 searches/month | SERP data, competitor discovery, Local Pack |
| Perplexity | Paid API | AEO visibility (Perplexity) |
| OpenAI | Paid API | AEO visibility (ChatGPT) |
| Google Cloud | Free tier | Knowledge Graph entity validation |

**10+ tools require zero API keys** — on-page analysis, technical audits, schema generation, citations, accessibility, product schema, media schema, international SEO, and geo tags all work immediately after install.

Configure keys after installing: `/plugin config seo-intelligence`

---

## FAQ

**Do I need to pay for this plugin?**
No. The plugin is free and open-source. External API keys are optional and only needed for SERP-based features.

**What is SerpAPI?**
[SerpAPI](https://serpapi.com/users/sign_up?source=seo-intelligence) provides real-time Google search results. Free tier: 100 searches/month — enough for ~30 keyword analyses with competitor comparisons.

**Does this store my data?**
No. Completely stateless. No data is stored, logged, or transmitted. All analysis happens in real-time in your Claude session.

**Can I use it without SerpAPI?**
Yes. On-page analysis, technical audits, schema generation, accessibility audits, product schema validation, and more work with zero API keys.

**How accurate is the SEO score?**
The score (0–100) evaluates on-page factors: meta tags, heading structure, content depth, schema, image optimization, internal links, FAQ presence, and Open Graph. It reflects on-page health, not domain authority or backlinks.

---

## Links

- **GitHub**: [github.com/trentiums/seo-intelligence](https://github.com/trentiums/seo-intelligence)
- **Workflows Guide**: [WORKFLOWS.md](./WORKFLOWS.md)
- **License**: [MIT](LICENSE)
- **Author**: Bhargav Patel — [github.com/trentiums](https://github.com/trentiums)
