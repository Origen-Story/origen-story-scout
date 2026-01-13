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
- Node.js 18+ (for dashboard)
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/Origen-Story/origen-story-scout.git
cd origen-story-scout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd dashboard
npm install
cd ..

# Configure environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

### Configuration

1. **Sources**: Copy `config/sources.example.yaml` to `config/sources.yaml` and add your RSS feeds
2. **Interests**: Copy `config/interests.example.yaml` to `config/interests.yaml` and customize your scoring topics
3. **Feeds (Optional)**: Export your feeds as OPML and save to `config/feeds.opml`

### Running

```bash
# Run the content pipeline (fetches, scores, summarizes)
python -m src.main run

# For development (uses mock data, skips archive)
python -m src.main run --dev --force

# Refresh mock data from live sources
python -m src.main refresh-dev

# Start the dashboard
cd dashboard
npm run dev
```

Then open http://localhost:5173 to view the dashboard.

## Project Structure

```
origen-story-scout/
├── src/
│   ├── main.py              # CLI entry point
│   ├── sources/             # RSS and Gmail ingestion
│   ├── processing/          # Filtering, trending detection
│   ├── llm/                 # Gemini integration
│   └── output/              # Report generation
├── dashboard/
│   ├── src/App.svelte       # Main dashboard component
│   └── public/data/         # Generated report JSON
├── config/                  # YAML configuration files
└── data/                    # Archive and mock data
```

## License

MIT License - see [LICENSE](LICENSE) for details.