# idocs.kz — Scrape Results (June 2026)

Example of using Firecrawl to document a competitor/own website.

## Site Structure (from firecrawl_map)

**Main pages:**
- Главная: https://idocs.kz
- Решения: https://idocs.kz/solutions
- Тарифы: https://idocs.kz/price
- КЭДО: https://idocs.kz/kedo
- Защита данных: https://idocs.kz/protection
- Контакты: https://idocs.kz/contacts
- Поддержка: https://idocs.kz/support
- API: https://idocs.kz/api
- FAQ: https://idocs.kz/faq
- Карьера: https://idocs.kz/career
- Новости: https://idocs.kz/news
- CustDev: https://idocs.kz/custdev
- Английская версия: https://idocs.kz/en
- Казахская версия: https://idocs.kz/kz

**Blog posts (30+):** covering EDO, KEDO, tax changes, HR tools, AI in business, cross-border document exchange, client cases (CDEK, Siemens, Wolt, Toyota, ERG, Nazarbayev University, Choco).

## Key Findings

### Pricing (from /price)
- Basic: 4,990 ₸/mo (up to 2 employees)
- Standard: 49,990 ₸/mo (3-100 employees) — most popular
- Pro: 399,990 ₸/mo (15-1,250 employees)
- Enterprise: custom pricing (unlimited)
- ЕСЭДО addon: 50,000 ₸/mo or 540,000 ₸/year
- КЭДО employees included: Basic=2, Standard=5, Pro=175, Enterprise=750

### Public Metrics (from homepage)
- 50,000+ clients
- 190,000 active users
- 7M+ signed documents

### Products
- Бухгалтерский ЭДО (with 1С integration)
- Кадровый ЭДО (КЭДО) — hiring, vacations, org structure, Enbek.kz integration
- ЕСЭДО — government document exchange
- API for embedding EDO into any IT solution
- Partner program

### Security (from /protection)
- Hosting: АО Казтелепорт (geo-distributed data centers, VMware VSphere)
- Encryption: AES256 at rest, HTTPS/SSL in transit, PBKDF2+HMAC-SHA256 for passwords
- Backups: daily incremental, weekly full, 7-week retention
- Firewall: FortiGate NGFW, VPN-only admin access
- Monitoring: Zabbix, Wazuh (SIEM), Nessus (vulnerability scanner), SOC
- Ratings: CyberGRX (Feb 2025), CyberVadis (Dec 2024)

### Legal Documentation (PDFs)
- Ministry of Finance clarification on E-documents in tax accounting
- Legal review of electronic document legal force in RK
- MCRIAP inquiry on cross-border EDO
- All hosted on Google Drive

### International
- Cross-border EDO with Russia (via Kontur.Diadok)
- English version at /en
- Kazakh version at /kz
- "Международный ЭДО" listed as option on all tariff plans

## Process Used

1. `firecrawl_map(url="https://idocs.kz")` → discovered ~130 URLs
2. `firecrawl_scrape` on 4 key pages (home, solutions, price, kedo, protection)
3. Rate limit hit on `firecrawl_crawl` — switched to map+selective scrape
4. Built DOCX with python-docx (see scripts/scrape_to_docx.py)
5. Total cost: ~6 Firecrawl credits for 5 scrapes + 1 map

## Lessons Learned

- Always `map` first before attempting `crawl`
- `onlyMainContent: true` is essential — otherwise Tilda CDN URLs flood output
- Rate limits: Firecrawl has per-minute limits; wait 30s between bulk operations
- For Tilda-based sites (like idocs.kz), markdown extraction works well but image URLs (tildacdn) should be stripped for readability
- `firecrawl_search_feedback` should be called after every `firecrawl_search` to get credit refund
