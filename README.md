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

This curator is configured for stories at the intersection of:
- AI + Journalism/Documentary/Filmmaking
- Generative AI tools (Sora, Runway, Midjourney, etc.)
- Digital provenance & C2PA/Content Credentials
- Climate tech & adaptation
- AI ethics & policy

## Setup

### Prerequisites
- Python 3.11+
- Google Gemini API key

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

1. Export your RSS feeds from Inoreader as OPML and save to `config/feeds.opml`
2. Customize your interests in `config/interests.yaml`
3. Run the curator:

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
