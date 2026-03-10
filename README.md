# Origen Story Scout

> **Work in Progress** — This project is under active development

An AI-powered content scout that aggregates information from RSS feeds and newsletters, analyzes relevance based on your interests, and surfaces the most important stories via a sleek dashboard.

## Features

### Current
- **Multi-source ingestion**: RSS feeds (via OPML import), Gmail newsletters
- **AI-powered summarization**: Using Google Gemini for content summaries
- **Personalized relevance scoring**: Based on configurable topic interests with keyword matching
- **Cross-source trending detection**: Identifies stories covered by multiple sources
- **Trending entity extraction**: Surfaces frequently mentioned companies, products, and people
- **Interactive dashboard**: Svelte-based UI with filtering, starring, and collapsible sections
- **Star/save functionality**: Save stories for later with localStorage persistence

### Planned
- **C2PA Provenance Verification**: Detect and display Content Credentials to verify content authenticity and origin
- **Creator Compensation Tracking**: Surface attribution and compensation information for original creators
- **Enhanced provenance indicators**: Visual trust signals based on verified content credentials
- **Additional content sources**: YouTube, Podcasts, Fediverse and other sources that incorporate C2PA and provenance information.

## Vision

Origen Story Scout is part of a broader mission to promote authentic, properly attributed content in the age of AI. By integrating C2PA (Coalition for Content Provenance and Authenticity) standards, we aim to:

- Help users identify verified, trustworthy sources
- Surface creator attribution and compensation information
- Combat misinformation by highlighting provenance-verified content
- Support the creative economy by making attribution visible

## Dashboard Preview

The dashboard displays:
- **Trending bar**: Clickable entity chips (OpenAI, Claude, ChatGPT, etc.) to filter stories
- **Cross-Source Coverage**: Stories covered by multiple outlets with direct source links
- **Story cards**: Top 9 stories with summaries, relevance scores, and star buttons
- **Additional stories**: Scrollable list of remaining stories

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- One LLM API key: Gemini, OpenAI, or Claude

### Installation

```bash
# Clone the repository
git clone https://github.com/Origen-Story/origen-story-scout.git
cd origen-story-scout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -e .

# Install frontend dependencies
cd frontend
npm install
cd ..

# Configure environment
cp .env.example .env
# Edit .env with your LLM API key (GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY)
```

### Configuration

1. **Sources**: Copy `config/sources.example.yaml` to `config/sources.yaml` and add your RSS feeds
2. **Interests**: Copy `config/interests.example.yaml` to `config/interests.yaml` and customize your scoring topics
3. **Feeds (Optional)**: Export your feeds as OPML and save to `config/feeds.opml`

### Running

```bash
# Start the frontend (view existing data)
cd frontend && npm run dev
# Then open http://localhost:5173

# Run the content pipeline (fetches, scores, generates report)
python -m backend.main run

# Regenerate report without re-fetching (useful after code changes)
python -m backend.main run --report-only
```

### CLI Commands

#### `python -m backend.main run`

Main command to fetch content and generate the report.

| Flag | Description |
|------|-------------|
| `--force` | Re-process already archived items (bypass the "already seen" check) |
| `--summarize` | Generate AI summaries for top stories (uses API tokens) |
| `--skip-ingest` | Skip fetching, reload from content cache (use with `--force` to re-analyze) |
| `--report-only` | Skip fetching, just refresh the report timestamp |
| `--dev` | Use mock data instead of fetching live RSS feeds |
| `--limit N` | Limit display output (default: 10) |

**Common usage patterns:**

```bash
# Daily run - fetch new content and cache it
python -m backend.main run --force

# Full run with AI summaries
python -m backend.main run --force --summarize

# Re-analyze cached content without re-fetching (iterate on scoring/summaries)
python -m backend.main run --skip-ingest --force --summarize

# Quick report refresh (no network calls, no re-analysis)
python -m backend.main run --report-only

# Development with mock data
python -m backend.main run --dev --force
```

#### `python -m backend.main refresh-dev`

Fetch live data and save to `data/mock_data.json` for development mode.

| Flag | Description |
|------|-------------|
| `--limit N` | Max items to save (default: 50) |

### Frontend

```bash
cd frontend
npm run dev      # Development server at http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
```

## Project Structure

```
origen-story-scout/
├── backend/
│   ├── main.py              # CLI entry point
│   ├── ingestion/           # RSS and Gmail ingestion
│   ├── scoring/             # Scoring, trending, provenance
│   └── summarizer/          # LLM provider routing
├── frontend/
│   ├── src/App.svelte       # Main dashboard component
│   └── public/data/         # Generated report JSON
├── shared/                  # Common types, config, utilities
├── config/                  # YAML configuration files
└── data/                    # Archive and mock data
```

## License

MIT License - see [LICENSE](LICENSE) for details.
