# SEO Intelligence — Your AI-Powered SEO Analyst Inside Claude

[![Anthropic Plugin](https://img.shields.io/badge/Anthropic-Plugin-blueviolet)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![BYOK](https://img.shields.io/badge/Model-BYOK-orange)](https://serpapi.com)

> **Turn Claude into a full-stack SEO expert.** Analyze any page, compare against competitors, and get a prioritized action plan to rank higher — all through natural conversation.

---

## What is SEO Intelligence?

SEO Intelligence is a **Claude MCP Plugin** that brings professional-grade SEO analysis directly into your Claude conversations. Instead of juggling multiple SEO tools and dashboards, simply ask Claude to analyze any webpage, and get actionable insights in seconds.

**No dashboards. No learning curve. Just type.**

The plugin embodies **20+ years of SEO expertise** codified into algorithms — gap analysis, ranking strategies, competitor benchmarking, and prioritized action plans — all powered by real-time SERP data.

---

## Key Features

### 🔍 On-Page SEO Analysis
Crawl any URL and get a comprehensive health check: title tags, meta descriptions, heading hierarchy (H1–H6), word count, internal/external links, image alt text coverage, FAQ detection, schema markup, Open Graph tags, and an overall **SEO score (0–100)**.

### 📊 Live SERP Data
Search Google in real time using SerpAPI. See who's ranking for your target keywords, what SERP features are present (featured snippets, People Also Ask, knowledge panels), and where opportunities exist.

### ⚔️ Competitor Gap Analysis
Automatically crawl and analyze the top-ranking pages for any keyword, then compare them against your page across content depth, heading structure, meta tags, FAQ sections, schema markup, link profiles, and image optimization.

### 📋 Prioritized Ranking Plans
Get a numbered, actionable plan with specific on-page changes, effort levels (Easy/Medium/Hard), expected impact (High/Medium/Low), and categories (meta, content, structure, schema, technical).

### ⚡ Quick Wins
Instantly surface the **5 easiest fixes with the biggest impact** — perfect for getting started or making quick progress. Examples: missing meta description, broken H1, no FAQ schema, missing alt text.

### 📝 Multi-Keyword Full Audit
Run a comprehensive SEO audit across multiple target keywords at once. Get per-keyword competitor comparisons, gap analyses, and individual ranking plans — plus an overall site SEO score.

### 🔑 API Key Validator
Verify your SerpAPI key is configured correctly before running analyses. Get setup instructions and sign-up links if anything is missing.

### 🛠️ Technical SEO Infrastructure Check
Check your site's technical SEO health — sitemap.xml, robots.txt, SSL/HTTPS, redirect chains, canonical tags, mobile readiness — and get pass/warn/fail for each check.

### 🧠 Search Intent & Content Briefs
Classify keywords (informational, transactional, etc.) and automatically generate SEO content briefs from competitor analysis — with titles, headings, word counts, and questions.

### 🔗 Keyword Strategy & Clustering
Group related keywords by SERP overlap to build content clusters. Detect keyword cannibalization where multiple pages compete for the same keyword.

### 🤖 AI Citation & AEO Tracking
Evaluate your domain's visibility across AI search engines like Perplexity, ChatGPT, and Google SGE to measure Answer Engine Optimization (AEO) success.

### 🏛️ Entity & Semantic SEO
Verify official Google Knowledge Graph entities and generate schema markup recommendations to build topical authority.

### 📈 Predictive Keyword Analytics
Estimate ranking difficulty, projected traffic, and ROI timelines based on deep competitor and domain authority analysis.

---

## Use Cases

### 1. Blogger / Content Creator
> *"I just published a new blog post. Is my SEO good enough to rank?"*

Ask Claude to `analyze_page` your post URL. You'll get an immediate SEO score, a breakdown of what's working (good heading structure, proper meta tags) and what's missing (no FAQ schema, thin content, missing alt text). Then ask for `quick_wins` to get the 5 fastest fixes.

**Example prompt:**
```
Analyze the SEO of https://myblog.com/best-coffee-brewing-methods and give me quick wins
```

---

### 2. Startup Founder
> *"We're launching a SaaS product. How do we stack up against competitors in search?"*

Use `compare_with_competitors` to see exactly where your landing page falls short versus the top 3 Google results for your target keyword. The gap analysis reveals whether competitors have longer content, better structured data, more FAQ coverage, or stronger link profiles.

**Example prompt:**
```
Compare https://myapp.com/features against competitors for "project management software"
```

---

### 3. Freelance SEO Consultant
> *"I need to deliver a professional SEO report to my client within the hour."*

Run a `full_audit` across all of your client's target keywords. Claude generates a structured, comprehensive report with per-keyword rankings, gap analyses, and prioritized action plans — ready to share with your client.

**Example prompt:**
```
Run a full SEO audit of https://clientsite.com for keywords: "custom wedding cakes", "wedding cake designs", "best wedding bakery near me"
```

---

### 4. E-Commerce Store Owner
> *"My product pages aren't showing up on Google. What am I doing wrong?"*

Analyze a product page with `analyze_page` to check for product schema markup, image optimization, content depth, and meta tag quality. Then use `generate_ranking_plan` to get a step-by-step plan for outranking competitors for your product keyword.

**Example prompt:**
```
Create a ranking plan for https://mystore.com/organic-matcha-powder targeting "best organic matcha powder"
```

---

### 5. Marketing Agency
> *"We manage 20 client websites. We need to scale SEO audits across all of them."*

Use Claude to run sequential `full_audit` calls across client domains. Each audit produces a complete report with scores, gaps, and plans. The BYOK model means each client can use their own SerpAPI key, keeping costs transparent.

**Example prompt:**
```
Run a full SEO audit of https://client1.com for keywords: "dental implants", "cosmetic dentistry"
```

---

### 6. Developer Building a Website
> *"I built a site with React/Next.js but I don't know SEO. Where do I start?"*

Start with `quick_wins` to get the 5 most impactful fixes, and run `technical_seo_audit` to ensure your infrastructure (SSL, robots.txt, sitemap) is correct. Then use `analyze_page` for a full breakdown of what search engines see when they crawl your page.

**Example prompt:**
```
Find quick SEO wins and run a technical audit for https://myportfolio.dev
```

---

### 7. Content Strategist
> *"I need to plan content clusters and write briefs for the writing team."*

Use `keyword_cluster` to group your keyword list by SERP overlap, ensuring you aren't creating cannibalizing pages. Then run `content_brief` on each primary keyword to get data-backed briefs with word count targets, headings, and questions to answer.

**Example prompt:**
```
Cluster these keywords: "cold brew coffee", "iced coffee", "cold brew recipe". Then generate a content brief for "how to make cold brew coffee"
```

---

## How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  You ask     │────▶│  Plugin crawls   │────▶│  Claude delivers │
│  Claude      │     │  pages & SERPs   │     │  insights & plan │
└─────────────┘     └──────────────────┘     └──────────────────┘
```

1. **You ask** — Type a natural language request in Claude (e.g., "Analyze the SEO of example.com")
2. **Plugin works** — SEO Intelligence crawls the target page, fetches live SERP data from Google, analyzes competitors, and runs gap analysis
3. **Claude responds** — You get a structured, actionable report with scores, comparisons, and a prioritized plan

---

## Available Tools

| Tool | Description | API Key Required? |
|------|-------------|:-----------------:|
| `analyze_page` | Full on-page SEO analysis of any URL | No |
| `search_serp` | Search Google and get top organic results | Yes (SerpAPI) |
| `compare_with_competitors` | Gap analysis vs. top-ranking pages | Yes (SerpAPI) |
| `generate_ranking_plan` | Prioritized action plan for a keyword | Yes (SerpAPI) |
| `quick_wins` | Top 5 easiest high-impact fixes | No |
| `full_audit` | Complete multi-keyword SEO audit | Yes (SerpAPI) |
| `check_api_keys` | Verify your API keys are configured | No |
| `technical_seo_audit` | Sitemap, robots.txt, SSL, redirects, canonical checks | No |
| `classify_intent` | Classify search intent (informational/transactional/etc.) | Yes (SerpAPI) |
| `content_brief` | Generate a content brief from competitor analysis | Yes (SerpAPI) |
| `keyword_cluster` | Group related keywords by SERP overlap | Yes (SerpAPI) |
| `detect_keyword_cannibalization` | Find pages competing for the same keywords | Yes (SerpAPI) |
| `check_aeo_visibility` | Check AI Answer Engine Optimization (AEO) | Optional (Perplexity/OpenAI) |
| `analyze_entity` | Search Google Knowledge Graph for entity validation | Optional (Google Cloud) |
| `predict_keyword_difficulty` | Estimate ranking difficulty and traffic potential | Yes (SerpAPI) |

---

## Pricing & Architecture

### BYOK — Bring Your Own Key

SEO Intelligence uses a **zero-cost architecture**. The plugin itself is **100% free**. You provide your own API keys for external data:

| Service | Cost to You | What It Powers |
|---------|-------------|----------------|
| Claude | Your existing Anthropic plan | Running the plugin |
| SerpAPI | Free tier: 100 searches/month | SERP data, competitor discovery |
| Perplexity (Optional) | Paid API | AEO visibility checking |
| OpenAI (Optional) | Paid API | ChatGPT indexing evaluation |
| Google Cloud (Optional) | Free tier | Knowledge Graph Entity validation |

> **4 tools work with zero configuration** — `analyze_page`, `quick_wins`, `check_api_keys`, and `technical_seo_audit` require no API keys at all.

---

## Getting Started

### Step 1: Install

**From Plugin Marketplace:**
```
/plugin install seo-intelligence@claude-plugin-directory
```

**Or manually:**
```bash
git clone https://github.com/trentiums/seo-intelligence.git
cd seo-intelligence/seo-plugin
uv sync
```

### Step 2: Configure Claude Desktop

Add to your Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "seo-intelligence": {
      "command": "uv",
      "args": ["--directory", "C:/path/to/seo-plugin", "run", "server.py"],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here",
        "PERPLEXITY_API_KEY": "your_optional_perplexity_key",
        "OPENAI_API_KEY": "your_optional_openai_key",
        "GOOGLE_CLOUD_API_KEY": "your_optional_google_key"
      }
    }
  }
}
```

### Step 3: Start Using

Restart Claude Desktop and try:
```
"Check my SEO plugin API keys"
"Analyze the SEO of https://example.com"
"Find quick SEO wins for https://mysite.com"
```

---

## FAQ

### Do I need to pay for this plugin?
**No.** The plugin is free and open-source (MIT License). You only pay for external APIs if you choose to use SERP-based tools. 4 out of 12 tools work with zero configuration.

### What is SerpAPI?
[SerpAPI](https://serpapi.com/users/sign_up?source=seo-intelligence) provides real-time Google search results data. Their free tier gives you **100 searches/month** — enough to analyze ~30 keywords with competitor comparisons.

### Does this plugin store my data?
**No.** SEO Intelligence is completely stateless. It doesn't store, log, or transmit any of your data. All analysis happens in real-time and results are returned directly to your Claude conversation.

### Can I use this without SerpAPI?
**Yes.** `analyze_page`, `quick_wins`, `check_api_keys`, and `technical_seo_audit` work without any API key. These tools crawl and analyze pages directly without needing SERP data.

### How accurate is the SEO score?
The SEO score (0–100) evaluates on-page factors: meta tags, heading structure, content depth, schema markup, image optimization, internal/external links, FAQ presence, and Open Graph tags. It reflects on-page health — not domain authority or backlink strength.

### Does it respect robots.txt?
**Yes.** The crawler uses a respectful User-Agent, honors timeouts, and follows ethical crawling practices.

---

## Links

- **GitHub**: [github.com/trentiums/seo-intelligence](https://github.com/trentiums/seo-intelligence)
- **License**: [MIT](LICENSE)
- **SerpAPI Sign-Up**: [serpapi.com](https://serpapi.com/users/sign_up?source=seo-intelligence)
- **Author**: Bhargav Patel

---

*Built with ❤️ for the Claude plugin ecosystem*
