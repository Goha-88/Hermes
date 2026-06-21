# Verified Skill Repository Paths

Path conventions and inventory as of June 2026. Verified by downloading and installing.

## daffy0208/ai-dev-standards (60+ skills)

Pattern: `skills/<skill-name>/SKILL.md`
Default branch: `main`

Verified skills (all installed and audited clean):
- brand-designer, brand-voice, copywriter, customer-feedback-analyzer, customer-support-builder
- data-engineer, data-visualizer, deployment-advisor, design-system-architect
- figma-developer, focus-session-manager, forensic-data-engineer, framework-orchestrator
- frontend-builder, go-to-market-planner, growth-experimenter
- iot-developer, knowledge-base-manager, knowledge-graph-builder
- livestream-engineer, localization-engineer, manifest-generator
- mobile-developer, multi-agent-architect, mvp-builder
- orchestration-planner, performance-optimizer, pricing-strategist
- product-analyst, product-analytics, product-strategist
- prototype-designer, prp-generator, quality-assurance, quality-auditor
- rag-implementer, release-manager, security-architect, security-engineer
- skill-validator, spatial-developer, supabase-developer
- system-diagnostician, task-breakdown-specialist, technical-writer
- testing-strategist, usability-tester, user-researcher, ux-designer
- video-producer, visual-designer, voice-interface-builder
- 3d-visualizer, accessibility-engineer, animation-designer
- api-designer, api-integration-builder, archon-manager, asset-manager
- audio-producer, bmad-method

## wshobson/agents (100+ plugins)

Pattern: `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
Default branch: `main`

Verified skills (subset):
- `plugins/brand-landingpage/skills/brand-landingpage/SKILL.md`
- `plugins/social-publishing/skills/social-publishing/SKILL.md`

Known plugins WITHOUT skill files (agents-only):
- business-analytics, content-marketing, customer-sales-automation, seo-analysis-monitoring, seo-content-creation, seo-technical-optimization, startup-business-analyst, full-stack-orchestration

Note: README claims skill files at `plugins/<plugin>/SKILL.md` — this is WRONG. Actual path is `plugins/<plugin>/skills/<skill>/SKILL.md`. Always probe with curl.

## apify/agent-skills

Pattern: `skills/<skill-name>/SKILL.md`
Default branch: `main`

Only 5 skills, all about Apify actor development:
- apify-actor-development, apify-actorization, apify-generate-output-schema, apify-sdk-integration, apify-ultimate-scraper

No market research, competitor monitoring, or general scraping skills despite the "agent-skills" name.

## shaom/brand-to-design-md-skill

Pattern: `skills/<skill-name>/SKILL.md`
Default branch: `main`

Single skill:
- brand-to-design (turns brand URL → DESIGN.md + optional HTML demo)

Install command: `npx skills add https://github.com/shaom/brand-to-design-md-skill --skill brand-to-design`

## vercel-labs/skills

Pattern: `<skill-name>/SKILL.md`
Default branch: `main`

Most useful skill here:
- find-skills (canonical installer; install with `npx skills add https://github.com/vercel-labs/skills --skill find-skills`)

## jeremylongshore/excel-analyst-pro-skill-md

Pattern: `skills/<skill-name>/SKILL.md`
Default branch: `main`

Financial modeling skills (DCF, LBO, variance, pivot):
- excel-dcf-modeler, excel-lbo-modeler, excel-pivot-wizard, excel-variance-analyzer

**Requires `@negokaz/excel-mcp-server`** — won't function without it. Document this before installing.

License: Intent Solutions Proprietary (not MIT-compatible).

## Curated collections (not single-skill repos)

| Repo | What it is |
|------|------------|
| `mxyhi/ok-skills` | Curated collection |
| `mohitagw15856/pm-claude-skills` | 180 PM-focused skills |
| `bergside/awesome-design-skills` | 67 design SKILL.md files |
| `narwhal-lab/MagicSkills` | Skill packaging tool |
| `agent-skills.md` (futantan) | Searchable skill directory |

## How to discover new repos

```python
# GitHub search query templates
"SKILL.md <domain> in:name,description,readme topic:agent-skills"
"<domain> topic:claude-skills"
"<domain> topic:codex-skills"
```

Use `mcp_github_search_repositories` with these queries, then check the resulting repos' structure with `firecrawl_scrape` before downloading.

## Path probing cheat sheet

When the SKILL.md path is unknown, try these in order:

```bash
# Most common
curl -sL -o test.md "https://raw.githubusercontent.com/<owner>/<repo>/main/skills/<name>/SKILL.md"

# wshobson pattern
curl -sL -o test.md "https://raw.githubusercontent.com/<owner>/<repo>/main/plugins/<name>/skills/<name>/SKILL.md"

# Root-level
curl -sL -o test.md "https://raw.githubusercontent.com/<owner>/<repo>/main/<name>/SKILL.md"

# Try both main and master
# If all 404, use Firecrawl to discover the path
```