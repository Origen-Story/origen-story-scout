# Origen Story Scout - Project Context

## Project Overview
AI-powered content curation tool that aggregates news from RSS feeds and Gmail newsletters, scores relevance based on user interests, and displays top stories in a Svelte dashboard.

## IMPORTANT: Module Boundary Rules

**When working on a module (e.g., scoring), do not modify files in other modules (e.g., frontend) without explicit user permission.**

This project uses a modular architecture to support future agentic workflows. Each module has a specific responsibility:

| Module | Responsibility | Can Modify |
|--------|----------------|------------|
| `backend/ingestion` | Fetch content from sources | Only ingestion files |
| `backend/scoring` | Score and rank content | Only scoring files |
| `backend/summarizer` | LLM summarization | Only summarizer files |
| `shared` | Common data types, config | Only with explicit permission |
| `frontend` | Web interface | Only frontend files |

**Cross-module changes require explicit user approval.**

---

## Architecture Overview

```
origen-story-scout/
├── backend/                    # Python backend modules
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── ingestion/              # Content source fetchers
│   │   ├── __init__.py
│   │   ├── rss.py              # RSS/Atom feed fetching
│   │   ├── gmail.py            # Gmail newsletter fetching
│   │   └── youtube.py          # YouTube transcript extraction
│   ├── scoring/                # Relevance and quality assessment
│   │   ├── __init__.py
│   │   ├── scorer.py           # Keyword-based relevance scoring
│   │   ├── trending.py         # Cross-source trending detection
│   │   └── provenance.py       # C2PA content authenticity
│   └── summarizer/             # LLM-based summarization
│       ├── __init__.py
│       ├── summarizer.py       # Summary orchestration
│       ├── base.py             # Base LLM interface
│       ├── gemini.py           # Google Gemini integration
│       ├── claude.py           # Anthropic Claude integration
│       └── router.py           # LLM routing logic
├── shared/                     # Shared data types and utilities
│   ├── __init__.py
│   ├── config.py               # Application configuration
│   ├── base.py                 # ContentItem dataclass
│   ├── report.py               # Report generation
│   └── storage/                # Persistence utilities
│       ├── __init__.py
│       └── archive.py          # Processed item tracking
├── frontend/                   # Svelte web interface
│   ├── src/
│   │   ├── App.svelte          # Main component
│   │   ├── app.css             # Styles
│   │   ├── main.js             # Entry point
│   │   └── lib/                # Utility modules
│   │       ├── starred.js      # Star/tag functionality
│   │       └── stats.js        # Usage statistics
│   ├── public/
│   │   └── data/
│   │       └── latest_report.json  # Generated report
│   ├── package.json
│   └── vite.config.js
├── config/                     # Configuration files
│   ├── interests.yaml          # Topics and keywords
│   ├── sources.yaml            # RSS feeds and Gmail settings
│   └── credentials.json        # Gmail OAuth credentials
├── data/                       # Runtime data
│   ├── archive.json            # Processed items tracking
│   └── mock_data.json          # Dev mode data
└── src/                        # DEPRECATED - being migrated
```

---

## Core Principles

### Cost Efficiency
- This is an ongoing app; minimize operational costs
- Prefer free/local solutions over paid APIs when quality is comparable
- API tokens should only be used when they provide clear value
- Budget time upfront for smarter solutions that save costs long-term

### Sustainability
- Avoid unnecessary API token consumption
- Cache results where possible
- Don't re-process items already in the archive
- Batch operations when feasible
- Use fast local filtering before expensive API calls

### Modularity
- Each module has a single responsibility
- Modules communicate through shared data types in `shared/`
- No direct imports between sibling modules (ingestion shouldn't import scoring)
- All inter-module communication goes through `shared/`

---

## Module Details

### backend/ingestion
**Purpose:** Fetch content from external sources

**Files:**
- `rss.py` - RSS/Atom feed parsing with feedparser
- `gmail.py` - Gmail API integration for newsletters
- `youtube.py` - YouTube transcript extraction

**Inputs:** Configuration from `shared/config.py`
**Outputs:** List of `ContentItem` objects

### backend/scoring
**Purpose:** Score content relevance and detect trends

**Files:**
- `scorer.py` - Keyword matching with word boundaries
- `trending.py` - Cross-source story clustering
- `provenance.py` - C2PA verification (currently disabled)

**Inputs:** List of `ContentItem` objects
**Outputs:** Scored items with `relevance_score` populated

### backend/summarizer
**Purpose:** Generate AI summaries using LLMs

**Files:**
- `summarizer.py` - Summary orchestration with caching
- `router.py` - LLM provider selection
- `gemini.py` / `claude.py` - Provider implementations

**Inputs:** High-scoring `ContentItem` objects
**Outputs:** Items with `summary` field populated

### shared
**Purpose:** Common types and utilities

**Files:**
- `config.py` - Settings loaded from YAML files
- `base.py` - `ContentItem` dataclass definition
- `report.py` - JSON report generation
- `storage/archive.py` - Deduplication tracking

### frontend
**Purpose:** Web-based dashboard

**Key Features:**
- 9-card grid for top stories
- Trending term filtering
- Star/tag system with localStorage
- Publication stats tracking
- Source type indicators

---

## CLI Commands

```bash
# Full pipeline (keyword scoring, free)
python -m backend.main run

# Use mock data (skip fetching)
python -m backend.main run --dev

# Re-process all items
python -m backend.main run --force

# Generate AI summaries (uses API tokens)
python -m backend.main run --summarize

# Refresh dev data from live sources
python -m backend.main refresh-dev
```

**Default behavior is FREE** - no API tokens used unless `--summarize` flag is passed.

---

## Data Flow

```
[RSS Feeds] ──┐
              ├──► [Ingestion] ──► [Scoring] ──► [Summarizer] ──► [Report] ──► [Frontend]
[Gmail]    ───┘         │              │             │
                        │              │             │
                        ▼              ▼             ▼
                   ContentItem    relevance_score  summary
```

---

## Configuration

### interests.yaml
Topics and keywords for scoring. Keywords use word-boundary matching.

### sources.yaml
RSS feed URLs and Gmail settings.

### .env
```
GEMINI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

---

## Development Workflow

```bash
# Start of day: refresh dev data from live sources
python -m backend.main refresh-dev

# During development: use cached dev data (fast, no network)
python -m backend.main run --dev

# Start frontend dev server
cd frontend && npm run dev
```

---

## Current Status
- RSS + Gmail ingestion: Working
- Keyword scoring: Working (word boundary matching)
- YouTube transcript extraction: Working
- Trending detection: Cross-source story clustering with score boost
- Star/save: LocalStorage-based starring with tags
- Dashboard: Fully interactive with source type indicators
- Summaries: Optional (requires API tokens)

## Future Features (Planned)
- Bluesky/Mastodon integration
- Podcast transcript integration
- Creator compensation tracking
- Newsletter export functionality
- C2PA manifest viewer
