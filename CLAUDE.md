# Origen Story Scout - Project Context

## Project Overview
AI-powered content curation tool that aggregates news from RSS feeds and Gmail newsletters, scores relevance based on user interests, and displays top stories in a Svelte dashboard.

## Core Principles

### Cost Efficiency
- This is an ongoing app; minimize operational costs
- Prefer free/local solutions over paid APIs when quality is comparable
- API tokens should only be used when they provide clear value over logic-based alternatives
- Budget time upfront for smarter solutions that save costs long-term

### Sustainability
- Avoid unnecessary API token consumption
- Cache results where possible
- Don't re-process items already in the archive
- Batch operations when feasible
- Use fast local filtering before expensive API calls

## Architecture Decisions

### Scoring Strategy (Two-Tier)
1. **Keyword scoring (free, local)** - Primary scoring method
   - Counts keyword matches from interests.yaml
   - Calculates breadth (topics hit) and depth (keywords per topic)
   - No API calls, instant results

2. **LLM semantic scoring (optional)** - Enhancement only
   - Only use when keyword scoring is insufficient
   - Should provide measurable improvement to justify cost

### Data Sources
- RSS feeds: 34 configured sources across 3 categories
- Gmail newsletters: Fetched via Gmail API from "Newsletters" label
- 10-day time window for all content
- Archive auto-prunes items older than 10 days

### Tech Stack
- **Backend**: Python 3.11+
- **Frontend**: Svelte 5 + Vite
- **LLM**: Gemini Flash (free tier), Claude as fallback
- **Storage**: JSON files (archive.json, latest_report.json)

## File Structure
```
src/
  main.py          - CLI entry point
  config.py        - Configuration loading
  sources/         - Data ingestion (RSS, Gmail)
  processing/      - Scoring, summarization, provenance
  output/          - Report generation
  storage/         - Archive management
dashboard/         - Svelte frontend
config/            - YAML configuration files
data/              - Runtime data (archive, mock data)
```

## CLI Commands
```bash
python -m src.main run              # Full pipeline (keyword scoring, free)
python -m src.main run --dev        # Use mock data (skip fetching)
python -m src.main run --force      # Re-process all items
python -m src.main run --use-llm    # Use LLM for semantic scoring (uses API tokens)
python -m src.main run --summarize  # Generate AI summaries (uses API tokens)
python -m src.main refresh-dev      # Fetch live data and save to mock_data.json
```

### Daily Development Workflow
```bash
# Start of day: refresh dev data from live sources
python -m src.main refresh-dev

# During development: use cached dev data (fast, no network)
python -m src.main run --dev
```

**Default behavior is FREE** - no API tokens used unless `--use-llm` or `--summarize` flags are passed.

## Configuration Files
- `config/interests.yaml` - Topics and keywords for scoring
- `config/sources.yaml` - RSS feeds and Gmail settings
- `.env` - API keys (GEMINI_API_KEY, ANTHROPIC_API_KEY)

## Current Status
- RSS + Gmail ingestion: Working
- Keyword scoring: Working
- LLM scoring: Available but hitting free tier limits
- Trending detection: Cross-source story clustering with score boost
- Star/save: LocalStorage-based starring with panel UI
- Dashboard: Fully interactive with trending badges and star functionality
- Summaries: Requires API tokens (optional)

## Future Features (Planned)
- Generate social posts from starred stories
- Group stories for newsletter sections
- Usage history tracking for source optimization
- Export starred stories to various formats