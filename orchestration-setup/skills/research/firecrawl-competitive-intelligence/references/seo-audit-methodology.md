# SEO Audit Methodology (Firecrawl)

Proven scoring framework used for idocs.kz (June 2026). Adapt for any website.

## Scoring Framework

| Category | Weight | What to Check |
|----------|--------|---------------|
| Technical SEO | 0-100 | robots.txt, sitemap, SSL, platform limitations |
| Meta Tags | 0-100 | Title, Description, OG tags, canonical, hreflang |
| Content | 0-100 | H1 presence, content depth, internal linking, clusters |
| URL Structure | 0-100 | Readability, /blog/ vs /tpost/, /page*.html garbage |
| Mobile | 0-100 | Viewport, responsive, srcset, AMP |
| Indexing | 0-100 | site: search, sitemap coverage %, schema.org |
| Social | 0-100 | OG image format, Twitter cards |

## Collection Steps

### Step 1: Technical Baseline
```
firecrawl_scrape(url="{site}/robots.txt", formats=["markdown"])
firecrawl_scrape(url="{site}/sitemap.xml", formats=["markdown"])
```

Check for:
- Sitemap references in robots.txt
- Escaped characters in sitemap (`\\_` → `_`)
- Date freshness of sitemap entries
- `Disallow` rules that might block important pages

### Step 2: Meta & Structure
```
firecrawl_scrape(url="{site}/", formats=["html"], onlyMainContent=false)
```

Extract from HTML:
- `<title>` — length, keyword placement
- `<meta name="description">` — length, CTA presence
- `<meta name="keywords">` — present but Google ignores
- `<link rel="canonical">` — CRITICAL if missing
- `<link rel="alternate" hreflang>` — CRITICAL for multilingual
- OG tags: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- `<h1>` — CRITICAL if missing on homepage

### Step 3: Index Coverage
```
web_search(query="site:{domain}")
```

Compare:
- Pages in Google index vs sitemap count
- % of site actually indexed
- Whether blog posts appear in index

### Step 4: Full Site Structure
```
firecrawl_map(url="{site}/")
```

Map all URLs. Flag:
- `/page*.html` — Tilda garbage URLs
- `/tpost/` — non-SEO-friendly blog URLs
- Missing language versions
- Duplicate content pages

### Step 5: Key Pages Content
```
firecrawl_scrape(url="{site}/solutions", formats=["markdown"])
firecrawl_scrape(url="{site}/price", formats=["markdown"])
firecrawl_scrape(url="{site}/blog-or-key-landing", formats=["markdown"])
```

Check for:
- H1 presence and keyword usage
- Content depth (thin vs substantial)
- Internal links between pages
- Duplicate content across pages

## Common Tilda-Specific Issues

1. **No H1 on homepage** — Tilda blocks don't automatically set H1
2. **No canonical URLs** — must be set manually in Tilda Settings → SEO
3. **No hreflang** — must be configured per language version
4. **Escaped underscores in sitemap** — `document\\_view` breaks indexing
5. **`/page*.html` in sitemap** — Tilda auto-generates these for every page
6. **`/tpost/` blog URLs** — non-SEO-friendly, consider redirects
7. **OG image as SVG** — social networks need PNG/JPEG (1200×630px)
8. **Images on tildacdn.pro** — external CDN loses SEO weight

## Report Template

```markdown
# SEO Audit: {Site}

**Date:** {date}
**Platform:** {detected CMS}
**Languages:** {list}

## Overall Score: X/100

| Category | Score | Status |
|----------|-------|--------|
| Technical | X/100 | 🟢/🟡/🔴 |
...

## Critical Issues (Top 5)
| # | Issue | Impact | Urgency |
|---|-------|--------|---------|

## Action Plan
### Immediate (today)
### This Week
### This Month

## Checklist for {Platform}
- [ ] Fix 1
- [ ] Fix 2
...
```
