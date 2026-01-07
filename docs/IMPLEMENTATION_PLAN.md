# AI Content Curator Agent - Implementation Plan

An intelligent agent that aggregates content from multiple sources, analyzes relevance based on your interests, and formats output for social media posts and newsletter drafting.

## User Review Required

> [!IMPORTANT]
> **API Key Storage**: Your Gemini API key will be stored in a `.env` file (gitignored). The `.env.example` template shows required variables without actual secrets.

> [!IMPORTANT]
> **Public Repository**: Since this will be a public GitHub repo for your portfolio, we'll follow security best practices:
> - All secrets in `.env` (gitignored)
> - Comprehensive `.gitignore` for Python + secrets
> - Clear README with setup instructions
> - Example config files (no personal feed URLs in tracked files)
> - MIT license for open source

> [!NOTE]
> **MVP Scope**: RSS feeds (via Inoreader OPML) + newsletter forwarding. Style matching, YouTube, podcasts, and interactive selection deferred to post-MVP.

---

## Project Structure

```
content-curator/
├── src/
│   ├── __init__.py
│   ├── main.py                 # CLI entry point
│   ├── config.py               # Configuration management
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract source interface
│   │   ├── rss.py              # RSS feed parser
│   │   └── newsletter.py       # Newsletter/email content parser
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py             # LLM abstraction interface
│   │   ├── gemini.py           # Google Gemini implementation
│   │   └── claude.py           # Anthropic Claude implementation
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── summarizer.py       # Content summarization
│   │   ├── scorer.py           # Relevance scoring
│   │   └── deduplicator.py     # Remove duplicate stories
│   ├── output/
│   │   ├── __init__.py
│   │   ├── formatter.py        # Output formatting
│   │   └── templates/          # Output templates
│   │       ├── social_post.md
│   │       └── newsletter_section.md
│   └── storage/
│       ├── __init__.py
│       └── archive.py          # Simple JSON-based storage
├── config/
│   ├── interests.yaml          # Your topic interests & weights
│   └── sources.yaml            # RSS feeds and source configuration
├── output/                     # Generated summaries go here
├── data/
│   └── newsletters/            # Drop newsletter files here
├── tests/
│   ├── __init__.py
│   ├── test_rss.py
│   ├── test_summarizer.py
│   └── test_scorer.py
├── .env.example                # Template for API keys
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Proposed Changes

### Component 1: Project Foundation

#### [NEW] [pyproject.toml](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/pyproject.toml)
Python project configuration with dependencies:
- `feedparser` - RSS/Atom feed parsing
- `beautifulsoup4` - HTML parsing for newsletters
- `google-generativeai` - Gemini API
- `anthropic` - Claude API (optional, for later)
- `pyyaml` - Configuration files
- `python-dotenv` - Environment variables
- `rich` - Beautiful CLI output
- `apscheduler` - For scheduling runs
- `click` - CLI framework

#### [NEW] [.env.example](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/.env.example)
Template showing required environment variables (GEMINI_API_KEY, optional ANTHROPIC_API_KEY)

#### [NEW] [.gitignore](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/.gitignore)
Standard Python gitignore plus `.env` and `output/` directory

---

### Component 2: Configuration System

#### [NEW] [config/interests.yaml](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/config/interests.yaml)
Your personalized interest configuration:
```yaml
topics:
  # Core intersection: AI meets storytelling
  - name: "AI + Journalism"
    keywords: ["AI journalism", "automated reporting", "newsroom AI", "news verification"]
    weight: 1.0
    
  - name: "AI + Documentary/Filmmaking"
    keywords: ["AI filmmaking", "AI documentary", "synthetic media", "AI cinematography"]
    weight: 1.0
  
  - name: "Generative AI Tools"
    keywords: ["Sora", "Runway", "Midjourney", "DALL-E", "Stable Diffusion", "AI video", "AI image", "LLM"]
    weight: 0.9
  
  - name: "Digital Provenance (C2PA)"
    keywords: ["C2PA", "content credentials", "content authenticity", "digital provenance", "deepfake detection"]
    weight: 1.0
  
  - name: "Climate Tech & Adaptation"
    keywords: ["climate adaptation", "climate tech", "carbon capture", "renewable energy", "climate AI"]
    weight: 0.8
  
  - name: "AI Ethics & Policy"
    keywords: ["AI regulation", "AI ethics", "AI policy", "AI safety"]
    weight: 0.7

preferences:
  time_window_days: 7          # Look back this many days
  min_relevance_score: 0.3     # Minimum score to include
  max_items_per_run: 20        # Cap on items to process deeply
  highlight_trending: true     # Flag high-coverage stories
  highlight_unique: true       # Flag low-coverage but high-interest stories
```

#### [NEW] [config/sources.yaml](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/config/sources.yaml)
Source configuration:
```yaml
# Import your Inoreader feeds via OPML
opml_file: "config/feeds.opml"  # Export from Inoreader, place here

# Or define feeds manually (these are examples, not tracked in git)
rss_feeds:
  - name: "Nieman Lab"
    url: "https://www.niemanlab.org/feed/"
    category: "journalism"
  
  - name: "MIT Tech Review - AI"
    url: "https://www.technologyreview.com/topic/artificial-intelligence/feed"
    category: "ai"

# Newsletter ingestion via email forwarding
newsletter_directory: "data/newsletters"
newsletter_formats: [".eml", ".html", ".txt"]
```

#### [NEW] [src/config.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/config.py)
Configuration loader that reads YAML files and environment variables

---

### Component 3: Data Ingestion

#### [NEW] [src/sources/base.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/sources/base.py)
Abstract base class defining the source interface:
```python
@dataclass
class ContentItem:
    id: str
    title: str
    content: str
    url: str
    source_name: str
    source_category: str
    published_date: datetime
    author: Optional[str]

class ContentSource(ABC):
    @abstractmethod
    def fetch(self) -> List[ContentItem]: ...
```

#### [NEW] [src/sources/opml.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/sources/opml.py)
OPML parser for Inoreader export:
- Parses OPML XML format
- Extracts feed URLs and titles
- Handles nested folder structures

**To get your feeds from Inoreader:**
1. Go to Inoreader → Settings → Import/Export
2. Click "Export to OPML"
3. Save the file as `config/feeds.opml`

#### [NEW] [src/sources/rss.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/sources/rss.py)
RSS feed parser using `feedparser`:
- Reads feeds from OPML or manual config
- Extracts title, content, link, date
- Handles various date formats
- Filters by time window

#### [NEW] [src/sources/newsletter.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/sources/newsletter.py)
Newsletter content parser:
- Scans `data/newsletters/` directory for forwarded emails
- Parses `.eml` files (standard email export format)
- Extracts clean text content using BeautifulSoup

**Newsletter forwarding setup (Gmail):**
1. Create a filter in Gmail for newsletters you want to track
2. Set filter action: "Forward to" a dedicated email OR "Apply label"
3. Periodically export labeled emails as `.eml` files to `data/newsletters/`
4. *(Post-MVP: Gmail API integration for automatic fetching)*

---

### Component 4: LLM Abstraction Layer

#### [NEW] [src/llm/base.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/llm/base.py)
Abstract LLM interface:
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str: ...
    
    @abstractmethod
    def summarize(self, content: str, max_length: int = 200) -> str: ...
```

#### [NEW] [src/llm/gemini.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/llm/gemini.py)
Google Gemini implementation using `google-generativeai`

#### [NEW] [src/llm/claude.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/llm/claude.py)
Anthropic Claude implementation (stub for future use)

---

### Component 5: Content Processing

#### [NEW] [src/processing/summarizer.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/processing/summarizer.py)
Content summarization pipeline:
- Takes raw content items
- Generates concise summaries via LLM
- Extracts key takeaways
- Identifies potential social media angles

#### [NEW] [src/processing/scorer.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/processing/scorer.py)
Relevance scoring system:
- Keyword matching against interests
- LLM-based semantic relevance scoring
- Coverage detection (is this topic trending?)
- "Unique angle" scoring: high interest + low coverage = opportunity

#### [NEW] [src/processing/deduplicator.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/processing/deduplicator.py)
Deduplication using title similarity and content hashing

---

### Component 6: Output Formatting

#### [NEW] [src/output/formatter.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/output/formatter.py)
Output generator with multiple formats:
- `format_for_social()` - Short-form drafts with hooks
- `format_for_newsletter()` - Longer summaries with context
- `format_digest()` - Full weekly digest in Markdown

#### [NEW] [src/output/templates/](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/output/templates/)
Markdown templates for consistent output formatting

---

### Component 7: Storage & CLI

#### [NEW] [src/storage/archive.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/storage/archive.py)
Simple JSON-based archive:
- Save items you've used
- Track what's been processed
- Export to Markdown for Notion/Docs

#### [NEW] [src/main.py](file:///C:/Users/mattf/.gemini/antigravity/scratch/content-curator/src/main.py)
CLI interface using Click:
```bash
# Run the curator and generate digest
python -m src.main run

# Run with specific output format
python -m src.main run --format social

# List configured sources
python -m src.main sources

# Save an item to archive
python -m src.main save <item-id>

# Schedule weekly runs
python -m src.main schedule --day monday --time 09:00
```

---

## Verification Plan

### Automated Tests

All tests use `pytest`. Run with:
```bash
cd content-curator
pytest tests/ -v
```

| Test File | What It Verifies |
|-----------|------------------|
| `test_rss.py` | RSS parsing works with sample feed data |
| `test_summarizer.py` | Summarization produces expected output format |
| `test_scorer.py` | Scoring algorithm ranks items correctly |

### Manual Verification

After implementation, we'll run these manual tests together:

1. **RSS Fetching Test**
   - Add 2-3 real RSS feeds to `config/sources.yaml`
   - Run `python -m src.main run --dry-run`
   - Verify items are fetched and displayed

2. **Full Pipeline Test**
   - Run `python -m src.main run`
   - Review generated `output/digest_YYYY-MM-DD.md`
   - Verify summaries are relevant and well-formatted

3. **Output Quality Check**
   - You review the social media drafts for usability
   - You review newsletter sections for your actual newsletter

---

## Implementation Order

1. **Project setup** (pyproject.toml, dependencies, config files)
2. **Configuration system** (load interests and sources)
3. **RSS source** (most critical data source)
4. **LLM layer** (Gemini integration)
5. **Summarizer** (core AI feature)
6. **Scorer** (relevance ranking)
7. **Output formatter** (usable output)
8. **Newsletter source** (secondary data source)
9. **CLI and scheduling** (automation)
10. **Archive storage** (save useful items)

## Source Complexity Analysis

| Source | Complexity | Notes |
|--------|------------|-------|
| RSS Feeds (OPML) | 🟢 Easy | Standard format, well-supported libraries |
| Newsletters (.eml) | 🟢 Easy | File-based, no API needed |
| Gmail API | 🟡 Medium | OAuth setup, but well-documented |
| YouTube Transcripts | 🟡 Medium | `youtube-transcript-api` library exists |
| Podcast Transcripts | 🟡 Medium | Need Whisper or paid service |
| BlueSky | 🟡 Medium | AT Protocol, relatively open |
| LinkedIn | 🔴 Hard | No official API for feed, ToS concerns |
| NYT (subscription) | 🔴 Hard | No public API, would need scraping |

**MVP recommendation:** RSS + Newsletter files. Gmail API is a good quick win for post-MVP.

---

## Post-MVP Roadmap

### Phase 2: Enhanced Ingestion
- [ ] Gmail API integration (auto-fetch newsletters)
- [ ] YouTube transcript summarization
- [ ] Podcast transcript summarization (via Whisper)

### Phase 3: Style & Personalization
- [ ] Writing style matching from your samples
- [ ] **Interactive selection mode**: Review summaries → select stories → generate draft
- [ ] Draft refinement with follow-up prompts

### Phase 4: Distribution
- [ ] BlueSky API integration
- [ ] Notion direct integration
- [ ] Scheduled email digest delivery

### Phase 5: Content Verification & Provenance
- [ ] **Cross-source corroboration** (MVP-adjacent): Flag story coverage count across sources
- [ ] Source reputation scoring (allowlist + credibility ratings)
- [ ] C2PA verification for media items (`c2pa-python` library)
- [ ] Integration with fact-check APIs (Google Fact Check, ClaimBuster)
- [ ] Claim extraction and verification pipeline

