---
name: firecrawl-competitive-intelligence
description: "Firecrawl MCP for competitive intelligence: scrape, map, crawl, monitor competitors and regulators, extract structured data, build lead lists, and generate DOCX reports."
version: 1.0.0
author: Hermes Agent (Карина)
tags: [firecrawl, competitive-intelligence, scraping, monitoring, leads, b2b, research, docx]
platforms: [linux, macos]
---

# Firecrawl Competitive Intelligence

Use Firecrawl (MCP server) for B2B competitive intelligence: scraping competitors, monitoring regulators, finding leads, and building structured reports. Firecrawl is a web scraping API with an MCP integration — all tools appear as `mcp_firecrawl_*`.

## When to Use

- Scrape a competitor's website for pricing, features, or messaging
- Build a site map to understand competitor site structure
- Monitor competitor/regulator sites for changes (pricing, new products, law changes)
- Extract structured data from multiple pages (pricing tables, feature lists)
- Find potential leads through web search + scraping
- Convert scraped content to DOCX/PDF reports

**Do not use** for quick web searches — use `web_search` or Perplexity `sonar` instead. Firecrawl is for structured extraction and deep crawling.

## Prerequisites

- Firecrawl MCP server must be configured (`hermes mcp list` — look for `firecrawl` with `✓ enabled`)
- If not configured: connect through the MCP marketplace or via `hermes mcp add`

## Tool Reference

### Quick Reference Table

| Tool | Use Case | Cost |
|------|----------|------|
| `firecrawl_search` | Web search with AI | 2 credits |
| `firecrawl_scrape` | Single page → markdown/JSON | 1 credit |
| `firecrawl_map` | Discover all URLs on a site | ~2 credits |
| `firecrawl_crawl` | Deep crawl multiple pages | Variable |
| `firecrawl_extract` | Structured data from pages | Variable |
| `firecrawl_monitor_create` | Recurring change detection | Per check |
| `firecrawl_agent` | Autonomous multi-step research | Variable (slow) |

### Detailed Tool Usage

**1. `firecrawl_scrape` — Single Page Extraction**

Best for getting content from a known URL. Use `markdown` format for reading, `json` for structured data.

```json
{
  "url": "https://competitor.kz/pricing",
  "formats": ["markdown"],
  "onlyMainContent": true
}
```

For structured extraction with a schema:

```json
{
  "url": "https://competitor.kz/pricing",
  "formats": ["json"],
  "jsonOptions": {
    "prompt": "Extract all pricing plans with name, price, and features",
    "schema": { "type": "object", "properties": { "plans": { "type": "array" } } }
  }
}
```

Always prefer `onlyMainContent: true` — strips navigation, footers, and noise.

**2. `firecrawl_map` — Discover Site Structure**

Use BEFORE crawling to understand the site. Returns all URLs with titles and descriptions.

```json
{
  "url": "https://competitor.kz",
  "search": "pricing"
}
```

The `search` parameter filters URLs by content — useful for finding specific pages.

**Workflow:** Map first → scrape key pages → avoid blind crawling.

**3. `firecrawl_crawl` — Deep Site Crawl**

⚠️ **Pitfall:** Crawl is rate-limited and can consume many credits. Start with small limits.

```json
{
  "url": "https://competitor.kz",
  "maxDiscoveryDepth": 2,
  "limit": 10,
  "allowExternalLinks": false,
  "scrapeOptions": { "formats": ["markdown"], "onlyMainContent": true }
}
```

If rate-limited: wait 30s, reduce `limit`, or use `map` + selective `scrape` instead.

**4. `firecrawl_search` — Web Search**

Like Google but with AI-powered results. Good for finding prospects.

```json
{
  "query": "компании Казахстана внедрение ЭДО 2026",
  "limit": 10,
  "sources": [{"type": "web"}]
}
```

Always call `firecrawl_search_feedback` after using results — refunds 1 credit and improves search quality.

**5. `firecrawl_monitor_create` — Ongoing Monitoring**

Create recurring checks (every 30 min by default) that detect changes on pages.

```json
{
  "page": "https://competitor.kz/pricing",
  "goal": "Alert when pricing, features, or plan structure changes. Ignore cosmetic updates.",
  "email": "gaukhar@idocs.kz"
}
```

Use `pages` array for multiple URLs. The `goal` controls what changes are flagged as meaningful.

**6. `firecrawl_extract` — Structured Data**

Extract specific data points from known pages. Best for pricing comparisons.

```json
{
  "urls": ["https://comp1.kz", "https://comp2.kz"],
  "prompt": "Extract company name, pricing plans, and key features",
  "schema": { "type": "object", "properties": { "companies": { "type": "array" } } }
}
```

**7. `firecrawl_agent` — Autonomous Research**

For complex multi-step research where you don't know the exact URLs. Async — submit, then poll `firecrawl_agent_status`.

```json
{
  "prompt": "Research the EDO market in Uzbekistan: key players, regulations, pricing",
  "schema": { "type": "object", "properties": { "market": { "type": "object" } } }
}
```

⚠️ **Pitfall:** Agent takes 1-5 minutes. Poll `firecrawl_agent_status` every 15-30s. Don't give up after 2-3 polls.

## Concrete Use Cases for B2B (idocs examples)

### 1. Competitor Pricing Intelligence

```
1. firecrawl_map(url="https://competitor.kz", search="price|tariff|pricing")
2. firecrawl_scrape on found pricing pages
3. Structure into comparison table
```

### 2. Regulatory Monitoring

```
firecrawl_monitor_create(
  pages=["https://adilet.zan.kz", "https://kgd.gov.kz"],
  goal="Alert on new regulations about electronic documents, EDO, digital signatures, or tax reporting"
)
```

### 3. Lead Generation

```
1. firecrawl_search(query="вакансия бухгалтер Казахстан site:hh.kz")
2. Extract company names from results
3. firecrawl_scrape on company websites for contact info
```

### 4. Full Site Documentation

Use the pattern: `map` → selective `scrape` → convert to DOCX (see scripts).

Command:
```bash
python3 scripts/scrape_to_docx.py --url https://target.kz --output report.docx
```

## Building DOCX Reports from Scraped Content

After scraping pages, generate a structured DOCX document. See `scripts/scrape_to_docx.py` for a reusable Python script that:
- Takes scraped markdown from multiple pages
- Formats as structured DOCX with headings, page breaks
- Includes a sitemap section with all URLs

Dependencies: `python-docx` (`pip install python-docx`).

**Execution pattern for long content:** When the DOCX content is too large for `execute_code`, write the Python script to file first, then run via terminal:
```bash
# Write script with write_file, then:
pip install python-docx -q && python3 build_docx.py
```
This avoids triple-quote escaping issues that plague inline execute_code blocks.

## SEO Audit with Firecrawl

For full SEO audits of any website, use this proven workflow (see `references/seo-audit-methodology.md` for the complete scoring framework):

1. **`firecrawl_scrape`** on `robots.txt` — check directives, sitemap references
2. **`firecrawl_scrape`** on `sitemap.xml` — count pages, check for escaped URLs (`\\_` bugs), verify dates
3. **`firecrawl_scrape`** with `formats: ["html"]` on homepage — extract all meta tags, OG tags, headings
4. **`web_search`** with `site:domain.kz` — check Google index vs sitemap
5. **`firecrawl_crawl`** or **`firecrawl_map`** — understand full site structure
6. Output as markdown report with scoring (0-100) per category: technical SEO, meta tags, content, URL structure, mobile, indexing, social

Common issues found on Tilda sites:
- Missing H1 on homepage (critical)
- Missing canonical URLs
- Missing hreflang for multilingual versions (ru/kz/en)
- Escaped underscores in sitemap (`\\_` instead of `_`)
- `/tpost/` blog URLs and `/page*.html` garbage in sitemap
- OG images in SVG (social networks require PNG/JPEG)
- No content clusters or internal linking between blog and product pages

## Using Perplexity for Market Research

For deep research on LLM models, market trends, or technology comparisons, use Perplexity's chat completions API directly (complementary to Firecrawl for search):

```bash
curl -s https://api.perplexity.ai/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -d '{"model":"sonar-pro","messages":[{"role":"user","content":"..."}]}'
```

`sonar-pro` ($5/1K queries + token costs) is ideal for research with citations. `sonar` is cheaper for simpler questions. The `perplexity-deep-research` skill covers the async deep-research endpoint for multi-minute investigations.

## Pitfalls

- ❌ **Blind crawling.** Always `map` first to understand site structure, then selectively scrape.
- ❌ **Too many crawl pages.** Start with `limit: 5`, increase only if needed. Rate limits are strict.
- ❌ **Scraping without `onlyMainContent`.** You'll get navigation, footers, and tracking scripts — useless noise.
- ❌ **Giving up on agent too early.** `firecrawl_agent` takes 1-5 minutes. Poll for at least 2-3 minutes.
- ❌ **Creating monitors without a goal.** Without `goal`, every whitespace change triggers an alert. Always set a meaningful `goal`.
- ❌ **Forgetting `firecrawl_search_feedback`.** It refunds 1 credit and improves search quality. Call it immediately after using search results.

## Related Skills

- `perplexity-deep-research` — async deep research with Perplexity (long-form, multi-minute)
- `blogwatcher` — RSS/Atom feed monitoring (simpler than Firecrawl monitors)
- `hermes-agent` — CLI reference for MCP server management

## Support Files

- `scripts/scrape_to_docx.py` — reusable script: takes scraped markdown pages and builds a structured DOCX report
- `references/idocs-scrape-example.md` — complete example: scraping idocs.kz (June 2026), including site structure, pricing, security details, and lessons learned
- `references/seo-audit-methodology.md` — step-by-step SEO audit workflow with scoring framework, collection steps, and Tilda-specific common issues
