# SEO Intelligence — Workflow Playbook

SEO Intelligence ships with **11 skills**, **3 agents**, **8 commands**, and **22 MCP tools**. True power comes from combining them to automate complex, multi-day SEO workflows into single Claude sessions.

---

## 1. Full Site SEO Audit

*Goal: Complete audit of a site with competitor analysis and action plan.*

**Fastest path — use the agent:**
```
"Run an SEO audit on https://mysite.com for keywords: best coffee maker, coffee machine reviews, coffee grinder reviews"
```
The **SEO Auditor** agent autonomously runs on-page analysis, technical check, SERP research, competitor gap analysis, and delivers a prioritized action plan.

**Manual step-by-step:**
1. `/seo-intelligence:technical-audit https://mysite.com` — infrastructure health first
2. `/seo-intelligence:seo-check https://mysite.com/page best coffee maker` — on-page score
3. `/seo-intelligence:competitor-gap https://mysite.com/page best coffee maker` — gap vs. top 3
4. `/seo-intelligence:ranking-plan https://mysite.com/page best coffee maker` — action plan

---

## 2. Content Strategy & Planning

*Goal: Build a full content calendar from a keyword list.*

**Fastest path — use the agent:**
```
"Build a content strategy for: cold brew coffee, iced coffee, cold brew recipe, cold brew vs iced coffee, best cold brew maker"
```
The **Content Strategist** agent clusters keywords, classifies intent, detects cannibalization, crawls competitors, and delivers production-ready briefs + a prioritized content calendar.

**Manual step-by-step:**
1. `/seo-intelligence:keyword-cluster cold brew coffee, iced coffee, cold brew recipe` — cluster + intent
2. `/seo-intelligence:content-brief how to make cold brew coffee` — brief for primary cluster
3. `/seo-intelligence:competitor-gap https://mysite.com/cold-brew cold brew coffee` — fill content gaps
4. Ask Claude: "Map internal links between these content clusters"

---

## 3. Competitor Research & Gap Analysis

*Goal: Find exactly why a competitor outranks you and how to close the gap.*

**Fastest path — use the agent:**
```
"Who is outranking me for 'best coffee maker' vs https://mysite.com/coffee and why?"
```
The **Competitor Analyzer** agent researches top 5 SERP results, crawls each, and delivers a ranked gap analysis with implementation instructions.

**Manual step-by-step:**
1. `/seo-intelligence:competitor-gap https://mysite.com/coffee best coffee maker`
2. Drill into top gap: "Generate schema markup for the types my competitors have"
3. `/seo-intelligence:ranking-plan https://mysite.com/coffee best coffee maker`

---

## 4. Local SEO Dominance

*Goal: Rank a local service page and build Local 3-Pack presence.*

```
"Analyze local SEO for my plumbing business 'Austin Plumbing Pro' in Austin TX for keywords: plumber near me, emergency plumber, 24 hour plumber"
```

Full workflow:
1. `/seo-intelligence:keyword-cluster plumber near me, emergency plumber, 24 hour plumber, commercial plumber` — find non-overlapping keyword variations
2. Local SEO skill auto-activates: 3-Pack presence check, citation list, LocalBusiness schema, geo tags
3. `/seo-intelligence:content-brief emergency plumber Austin TX` — page content brief
4. `/seo-intelligence:generate-schema https://mysite.com/plumber LocalBusiness` — full schema block
5. Ask Claude: "Give me citation opportunities for Austin Plumbing Pro at 123 Main St, Austin TX"

---

## 5. E-Commerce Product Page Optimization

*Goal: Win rich snippets and outrank the top product competitor.*

```
/seo-intelligence:seo-check https://mystore.com/organic-matcha best organic matcha powder
```

Full workflow:
1. `/seo-intelligence:technical-audit https://mystore.com/organic-matcha` — check canonical, robots.txt not blocking
2. E-commerce SEO skill auto-activates on product URL: validates Product schema, flags missing price/rating/availability
3. `/seo-intelligence:competitor-gap https://mystore.com/organic-matcha best organic matcha powder` — gap vs. top sellers
4. `/seo-intelligence:generate-schema https://mystore.com/organic-matcha Product` — corrected Product JSON-LD
5. Ask Claude: "Validate VideoObject schema if I have a product demo video"

---

## 6. Post-Algorithm Drop Recovery

*Goal: Recover rankings after a core update tanks a flagship page.*

```
"Why did https://myblog.com/coffee-guide drop for 'best coffee guide' and how do I recover?"
```

Full workflow:
1. Ask Claude: "Search SERP for 'best coffee guide' — who took my spot?" (uses `search_serp`)
2. `/seo-intelligence:keyword-cluster best coffee guide, coffee guide, coffee buying guide` — check if intent shifted
3. `/seo-intelligence:competitor-gap https://myblog.com/coffee-guide best coffee guide` — gap vs. new winners
4. `/seo-intelligence:ranking-plan https://myblog.com/coffee-guide best coffee guide` — exact rewrite priority list
5. Ask Claude: "What's the search intent for 'best coffee guide' now vs. 6 months ago?"

---

## 7. AI Search Readiness (AEO)

*Goal: Ensure your brand is cited by AI search engines, not just Google.*

```
"Check my AI search visibility for domain myblog.com for queries: best coffee maker, coffee grinder reviews"
```

Full workflow:
1. AEO visibility skill auto-activates: checks Perplexity, ChatGPT, Google SGE citations
2. Ask Claude: "Check my brand entity in Google Knowledge Graph" (uses `analyze_entity`)
3. `/seo-intelligence:generate-schema https://myblog.com Article` — add Speakable schema for voice/AI
4. `/seo-intelligence:content-brief what is the best coffee maker` — target long-tail question formats that feed LLM training
5. Ask Claude: "What content improvements would increase my AEO citation rate?"

---

## 8. International / Multilingual Launch

*Goal: Launch in a new language/country without duplicate content penalties.*

```
"Check the international SEO setup for https://mystore.com/en-us before we launch French and German versions"
```

Full workflow:
1. International SEO skill auto-activates: validates `hreflang`, `lang` attribute, x-default, reciprocal tags
2. `/seo-intelligence:technical-audit https://mystore.com/fr-fr` — check new locale pages
3. `/seo-intelligence:seo-check https://mystore.com/fr-fr meilleure cafetière` — on-page for French keyword
4. Ask Claude: "Generate corrected hreflang implementation for en-US, fr-FR, de-DE"
5. Accessibility skill: "Check WCAG compliance on my translated pages"

---

## 9. New Site Launch Checklist

*Goal: Launch a new site with all SEO fundamentals correct from day one.*

```
"Run a complete launch SEO audit for https://mynewsite.com"
```

Full workflow:
1. `/seo-intelligence:technical-audit https://mynewsite.com` — sitemap, robots.txt, SSL, redirects
2. `/seo-intelligence:seo-check https://mynewsite.com target keyword` — on-page score
3. `/seo-intelligence:generate-schema https://mynewsite.com` — add appropriate schema
4. Ask Claude: "Check accessibility and UX issues on https://mynewsite.com"
5. `/seo-intelligence:keyword-cluster [primary keywords]` — build content cluster map
6. `/seo-intelligence:content-brief [primary keyword]` — first content brief

---

## 10. Client SEO Reporting (Agency Workflow)

*Goal: Generate professional SEO audit reports for multiple clients fast.*

```
"Run an SEO audit on https://client1.com for keywords: dental implants, cosmetic dentistry, teeth whitening near me"
```

Repeat per client. The **SEO Auditor** agent delivers a structured report per client with:
- Overall SEO score
- Technical health checklist
- Per-keyword competitor comparison
- Prioritized action plan
- Quick wins section

For a content report:
```
"Build a content strategy for https://client1.com targeting: dental implants, cosmetic dentistry, dental veneers"
```

---

## Quick Reference

| Goal | Best approach |
|------|--------------|
| Full site audit | SEO Auditor agent |
| Content calendar | Content Strategist agent |
| Competitor research | Competitor Analyzer agent |
| Quick page check | `/seo-intelligence:seo-check` |
| Fix technical issues | `/seo-intelligence:technical-audit` |
| Rank higher for keyword | `/seo-intelligence:ranking-plan` |
| Plan content | `/seo-intelligence:content-brief` |
| Group keywords | `/seo-intelligence:keyword-cluster` |
| Add schema | `/seo-intelligence:generate-schema` |
| Local SEO | Local SEO skill (auto) |
| AI search visibility | AEO skill (auto) |
| International SEO | International SEO skill (auto) |
