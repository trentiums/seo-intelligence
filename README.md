# SEO Intelligence — Claude MCP Plugin

[![Anthropic Plugin](https://img.shields.io/badge/Anthropic-Plugin-blueviolet)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **AI-powered SEO analysis, competitor comparison, and ranking plans — right inside Claude.**

## What Does It Do?

SEO Intelligence is a Claude plugin that turns Claude into your SEO analyst. Give it any URL and target keywords, and it will:

- 🔍 **Analyze** your page's SEO health (title, meta, headings, content, schema, images, links)
- 📊 **Search** Google SERPs to find who's ranking above you
- ⚔️ **Compare** your page against top-ranking competitors
- 📋 **Generate** a prioritized action plan to rank higher
- ⚡ **Find quick wins** — the 5 easiest fixes with biggest impact
- 📝 **Full audit** — comprehensive analysis across multiple keywords

## Use Cases

| Who | Scenario | Tools Used |
|-----|----------|------------|
| **Blogger** | Check if a new post is SEO-ready, get the 5 fastest fixes | `analyze_page`, `quick_wins` |
| **Startup Founder** | See how your landing page stacks up against competitors | `compare_with_competitors` |
| **Freelance SEO Consultant** | Generate professional audit reports for clients in minutes | `full_audit` |
| **E-Commerce Owner** | Optimize product pages to outrank competitors for buying keywords | `generate_ranking_plan` |
| **Marketing Agency** | Run bulk audits across multiple client websites | `full_audit` (per client) |
| **Developer** | Check technical SEO infrastructure (sitemap, robots.txt, SSL) | `technical_seo_audit` |
| **Content Strategist** | Generate data-backed content briefs from competitor analysis | `content_brief` |
| **SEO Manager** | Find keyword cannibalization and build topic clusters | `keyword_cluster`, `detect_keyword_cannibalization` |

> 📄 **See [PLUGIN_HOMEPAGE.md](PLUGIN_HOMEPAGE.md) for detailed use-case walkthroughs with example prompts.**

## Quick Start

### Option A: Install from Plugin Marketplace (Recommended)

In Claude Code, run:
```
/plugin install seo-intelligence@claude-plugin-directory
```

Or browse: `/plugin > Discover > search "seo-intelligence"`

### Option B: Manual Installation

#### Prerequisites

- [Claude Desktop](https://claude.ai/download) installed
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (Python package manager)
- A [SerpAPI key](https://serpapi.com/users/sign_up?source=seo-intelligence) (free tier: 100 searches/month)

#### Step 1: Install the Plugin

Clone or download this folder, then install dependencies:

```bash
cd seo-plugin
uv sync
```

#### Step 2: Configure Claude Desktop

Open your Claude Desktop config file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the SEO Intelligence server:

```json
{
  "mcpServers": {
    "seo-intelligence": {
      "command": "uv",
      "args": ["--directory", "C:/path/to/seo-plugin", "run", "server.py"],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

> **Replace** `C:/path/to/seo-plugin` with the actual path to this folder.

#### Step 3: Restart Claude Desktop

After saving the config, restart Claude Desktop. You should see the SEO Intelligence tools available.

## Available Tools

| Tool | What It Does | Needs API Key? |
|------|-------------|----------------|
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

## Example Prompts

Try these in Claude:

```
"Check my SEO plugin API keys"

"Analyze the SEO of https://example.com"

"Find quick SEO wins for https://mysite.com/blog/my-post"

"Compare https://mysite.com/coffee against competitors for 'best coffee maker'"

"Create an SEO ranking plan for https://mysite.com targeting 'coffee machine reviews'"

"Run a full SEO audit of https://mysite.com for keywords: 'best coffee maker', 'coffee machine reviews'"

"Run a technical SEO audit on https://mysite.com"

"What's the search intent for 'best coffee maker 2026'?"

"Generate a content brief for 'how to make cold brew coffee'"

"Cluster these keywords: cold brew coffee, iced coffee, cold brew recipe, cold brew vs iced coffee"

"Check if example.com has keyword cannibalization for: coffee maker, best coffee maker, coffee maker reviews"
```

## API Keys

### SerpAPI (Required for SERP tools)

- **Free tier**: 100 searches/month — enough to analyze ~30 keywords
- **Sign up**: [serpapi.com/users/sign_up](https://serpapi.com/users/sign_up?source=seo-intelligence)
- **Paid plans**: Starting at $50/month for 5,000 searches
- **Used by**: `search_serp`, `compare_with_competitors`, `generate_ranking_plan`, `full_audit`

Tools that don't need an API key (`analyze_page`, `quick_wins`, `check_api_keys`) work immediately with zero configuration.

## Development

### Run Tests

```bash
cd seo-plugin
uv run pytest tests/ -v
```

### Project Structure

```
seo-intelligence/
├── server.py        # MCP entry point — 12 tools
├── crawler.py       # Page crawling & HTML parsing
├── serp.py          # SerpAPI integration
├── analyzer.py      # Gap analysis, scoring, plans, intent classification
├── technical.py     # Technical SEO audit (sitemap, robots, SSL, redirects)
├── content.py       # Content briefs, keyword clustering, cannibalization
├── models.py        # Data models (dataclasses)
├── pyproject.toml   # Dependencies
├── README.md        # This file
├── .env.example     # API key template
└── tests/
    ├── test_crawler.py
    ├── test_analyzer.py
    ├── test_serp.py
    ├── test_technical.py
    └── test_content.py
```

## Contributing

Pull requests welcome! See the [plugin submission form](https://clau.de/plugin-directory-submission) for getting listed on the official Anthropic marketplace.

## License

MIT
