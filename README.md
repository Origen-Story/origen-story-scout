# Origen Story Scout

> 🚧 **Work in Progress** — This project is under active development

An AI-powered content scout that aggregates information from RSS feeds and newsletters, analyzes relevance based on your interests, and surfaces the most important stories for social media posts and newsletter drafting.

## Features (Planned)

- 📡 **Multi-source ingestion**: RSS feeds (via OPML import), newsletters
- 🤖 **AI-powered summarization**: Using Google Gemini (Claude support planned)
- 🎯 **Personalized relevance scoring**: Based on configurable topic interests
- 📊 **Cross-source corroboration**: Identifies trending vs unique stories
- ✍️ **Content creator focused**: Output optimized for social posts and newsletters

## Topics of Interest

This curator is designed to be configured for any set of interests. Example topics might include:
- Technology & Innovation (AI, Robotics, Software)
- Science & Environment (Climate, Biology, Space)
- Business & Finance (Economy, Markets, Startups)
- Culture & Society (Media, Arts, Trends)

## Setup

### Prerequisites
- Python 3.11+
- API key for your chosen LLM (e.g., Google Gemini)

### Installation

```bash
# Clone the repository
git clone https://github.com/Origen-Story/origen-story-scout.git
cd origen-story-scout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

1. **Sources**: Copy `config/sources.example.yaml` to `config/sources.yaml` and add your RSS feeds or newsletter paths.
2. **Interests**: Copy `config/interests.example.yaml` to `config/interests.yaml` and customize your scoring topics.
3. **Feeds (Optional)**: If you use Inoreader, export your feeds as OPML and save to `config/feeds.opml`.

Run the curator:

```bash
python -m src.main run
```

## Project Status

- [x] Project setup
- [ ] RSS feed ingestion
- [ ] Newsletter ingestion  
- [ ] Gemini integration
- [ ] Content summarization
- [ ] Relevance scoring
- [ ] Output formatting

## License

MIT License - see [LICENSE](LICENSE) for details.
