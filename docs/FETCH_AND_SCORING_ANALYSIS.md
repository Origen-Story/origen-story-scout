# Origen Story Scout: Fetch Approach & Scoring Analysis

This document provides a comprehensive analysis of the current content fetching approach and scoring algorithm used by Origen Story Scout. It outlines what data is currently being captured, what could potentially be captured, and the benefits and limitations of each approach.

---

## Table of Contents
1. [Content Fetching by Type](#content-fetching-by-type)
   - [RSS Feeds](#rss-feeds)
   - [YouTube Channels](#youtube-channels)
   - [Podcasts](#podcasts)
   - [GitHub Releases](#github-releases)
   - [Gmail Newsletters](#gmail-newsletters)
2. [Scoring Approach](#scoring-approach)
   - [Algorithm Overview](#algorithm-overview)
   - [Why This Approach](#why-this-approach)
   - [Benefits and Drawbacks](#benefits-and-drawbacks)
   - [Potential Biases and Blind Spots](#potential-biases-and-blind-spots)
3. [Alternative Approaches](#alternative-approaches)
4. [Recommendations](#recommendations)

---

## Content Fetching by Type

### RSS Feeds

**Current Implementation:** `src/sources/rss.py`
**Source Count:** 42 configured feeds across 9 categories

#### What IS Being Fetched

| Field | Source | Notes |
|-------|--------|-------|
| Title | `entry.title` | Direct extraction |
| Summary/Description | `entry.summary` or `entry.description` | First available, truncated to 5000 chars |
| URL | `entry.link` or `entry.id` | Fallback to ID if no link |
| Author | `entry.author` | May be empty |
| Published Date | `entry.published_parsed` | Falls back to current time if missing |
| Media Link | `entry.links` or `media:content` | First image/enclosure found |
| Source Metadata | Configuration | Feed name and category |

#### What is NOT Being Fetched

| Field | Potential Value | Difficulty to Implement |
|-------|-----------------|-------------------------|
| **Full article content** | Better keyword matching, more context | Medium - requires HTTP fetch + HTML parsing |
| **RSS categories/tags** | Pre-labeled topic hints | Low - already in feed data |
| **Comment counts** | Engagement signal | Low - available in some feeds |
| **Enclosure metadata** | File type, size, duration | Low - already in feed data |
| **Language** | Filter non-English content | Medium - requires language detection |
| **Reading time estimate** | User prioritization | Low - calculate from word count |

#### Benefits of Current Approach

- **Fast:** No additional HTTP requests beyond feed fetch
- **Reliable:** Standard RSS parsing with feedparser library
- **Low resource:** Minimal memory and bandwidth usage
- **Broad compatibility:** Works with any RSS 2.0 or Atom feed

#### Limitations

- **Shallow content:** Only title and summary available for matching
- **Missing context:** Articles with short summaries may score poorly
- **No engagement data:** Can't prioritize popular content
- **Media gaps:** Only extracts first media item, misses rich media feeds

#### Potential Improvements

1. **Full content fetch:** Follow links to extract article body
   - *Benefit:* Much richer keyword matching, better scoring accuracy
   - *Drawback:* 10-20x slower, requires HTML parsing per article, may hit rate limits

2. **Feed category extraction:** Parse RSS category tags
   - *Benefit:* Pre-labeled topics could boost relevant matching
   - *Drawback:* Inconsistent tagging across feeds

---

### YouTube Channels

**Current Implementation:** Fetched as RSS feeds via YouTube's RSS endpoint
**Source Count:** 15 configured channels

#### What IS Being Fetched

| Field | Source | Notes |
|-------|--------|-------|
| Video Title | RSS entry title | Direct extraction |
| Description | RSS entry summary | First ~200 characters only |
| URL | RSS entry link | YouTube watch URL |
| Published Date | RSS entry date | Upload timestamp |
| Thumbnail | Media content | Low-resolution thumbnail |

#### What is NOT Being Fetched

| Field | Potential Value | Difficulty to Implement |
|-------|-----------------|-------------------------|
| **Video transcript** | Full spoken content for matching | Medium - YouTube API or whisper |
| **View count** | Popularity signal | Low - YouTube API |
| **Like/comment count** | Engagement signal | Low - YouTube API |
| **Video duration** | Filter by length | Low - YouTube API |
| **Channel metadata** | Subscriber count, category | Low - YouTube API |
| **Captions/subtitles** | Accessibility, more text | Medium - YouTube API |
| **Tags/keywords** | Creator-provided topics | Low - YouTube API |

#### Benefits of Current Approach

- **No API key required:** YouTube RSS feeds are public
- **No quota limits:** Unlike YouTube Data API
- **Same pipeline:** Reuses RSS fetching infrastructure
- **Fast:** Single feed fetch per channel

#### Limitations

- **Description truncation:** YouTube RSS provides only ~200 chars
- **No transcripts:** Missing 99% of video content
- **No popularity data:** Can't prioritize trending videos
- **No filtering by duration:** Can't distinguish shorts from long-form

#### Potential Improvements

1. **YouTube Data API integration:**
   - *Benefit:* Access to view counts, full descriptions, tags, duration
   - *Drawback:* Requires API key, 10,000 quota units/day limit, API complexity

2. **Transcript extraction via youtube-transcript-api:**
   - *Benefit:* Full spoken content for keyword matching (10-50x more text)
   - *Drawback:* Significantly slower (1-2 sec per video), not all videos have transcripts

3. **Whisper transcription for videos without captions:**
   - *Benefit:* Universal transcript availability
   - *Drawback:* Requires downloading audio, GPU for fast processing, storage

**Recommendation:** Transcript extraction would dramatically improve relevance scoring for video content. A 10-minute video might have 1500+ words of content vs. 30 words in the RSS description.

---

### Podcasts

**Current Implementation:** Fetched as RSS feeds
**Source Count:** 8 podcast feeds (AI + Climate)

#### What IS Being Fetched

| Field | Source | Notes |
|-------|--------|-------|
| Episode Title | RSS entry title | Usually descriptive |
| Show Notes | RSS entry description | Varies wildly in length |
| Audio URL | RSS enclosure | Direct link to MP3/AAC |
| Published Date | RSS entry date | Release timestamp |
| Duration | iTunes duration tag | When available |

#### What is NOT Being Fetched

| Field | Potential Value | Difficulty to Implement |
|-------|-----------------|-------------------------|
| **Transcript** | Full episode content | High - requires speech-to-text |
| **Chapter markers** | Topic-specific segments | Low - if in RSS feed |
| **Guest names** | People mentioned | Medium - NER extraction |
| **Show metadata** | Series description, category | Low - in feed |
| **Episode number** | Series tracking | Low - in feed |

#### Benefits of Current Approach

- **Fast:** Single RSS fetch
- **Show notes often rich:** Podcast feeds typically have detailed descriptions
- **No audio processing:** Avoids heavy compute requirements

#### Limitations

- **Show notes vary wildly:** Some podcasts have 2000-word show notes, others have 20 words
- **No spoken content:** Missing hours of discussion
- **Guest expertise lost:** Can't match on guest names/credentials
- **Topic depth unknown:** Can't tell if topic is 5-minute segment or full episode

#### Potential Improvements

1. **Whisper transcription:**
   - *Benefit:* Full episode content (5,000-15,000 words per hour)
   - *Drawback:* Requires downloading audio (50-100MB), GPU transcription (5-15 min/episode), storage

2. **Podcast index API:**
   - *Benefit:* Standardized metadata, chapter markers, transcript links
   - *Drawback:* Not all podcasts indexed, API registration required

3. **Guest name extraction:**
   - *Benefit:* Filter by expert guests
   - *Drawback:* Inconsistent formatting in titles

**Recommendation:** Given compute costs, focus on improving show note extraction quality rather than full transcription. Consider flagging episodes with minimal show notes for manual review.

---

### GitHub Releases

**Current Implementation:** Fetched as Atom feeds from GitHub releases
**Source Count:** 7 repository release feeds

#### What IS Being Fetched

| Field | Source | Notes |
|-------|--------|-------|
| Release Title | Atom entry title | Usually version number |
| Release Notes | Atom entry content | Full changelog/description |
| URL | Atom entry link | GitHub release page |
| Published Date | Atom entry updated | Release timestamp |
| Author | Atom entry author | Usually repository owner |

#### What is NOT Being Fetched

| Field | Potential Value | Difficulty to Implement |
|-------|-----------------|-------------------------|
| **Download count** | Popularity signal | Low - GitHub API |
| **Asset list** | What's included in release | Low - GitHub API |
| **Commit history** | What changed | Medium - GitHub API |
| **Pre-release flag** | Stability indicator | Low - GitHub API |
| **Repository stars** | Project popularity | Low - GitHub API |
| **Dependencies** | Related projects | Medium - parsing |

#### Benefits of Current Approach

- **No authentication:** Atom feeds are public
- **Rich release notes:** GitHub displays full markdown
- **Immediate updates:** Atom feeds update in real-time

#### Limitations

- **No popularity data:** Can't prioritize widely-used releases
- **No stability indicators:** Pre-releases mixed with stable
- **Version parsing required:** "v1.2.3" format varies

#### Potential Improvements

1. **GitHub API integration:**
   - *Benefit:* Download counts, assets, pre-release flags
   - *Drawback:* Rate limits (60/hour unauthenticated, 5000/hour with token)

2. **Star count weighting:**
   - *Benefit:* Prioritize releases from popular projects
   - *Drawback:* Requires additional API call per repository

---

### Gmail Newsletters

**Current Implementation:** `src/sources/gmail.py`
**Source Count:** Variable (based on user's subscriptions)

#### What IS Being Fetched

| Field | Source | Notes |
|-------|--------|-------|
| Subject | Email header | Becomes title |
| Body | Email content | HTML converted to text, max 5000 chars |
| Sender | From header | Becomes source name |
| Date | Date header | Send timestamp |
| Gmail URL | Reconstructed | Link back to message |

#### What is NOT Being Fetched

| Field | Potential Value | Difficulty to Implement |
|-------|-----------------|-------------------------|
| **Embedded links** | Articles referenced | Low - HTML parsing |
| **Attachments** | PDFs, documents | Medium - MIME handling |
| **Images** | Visual content | Medium - image extraction |
| **Read status** | User engagement | Low - Gmail API |
| **Labels** | User categorization | Low - Gmail API |

#### Benefits of Current Approach

- **Full content access:** Entire newsletter body available
- **Personalized sources:** User's actual subscriptions
- **Rich text:** Better keyword matching than RSS summaries

#### Limitations

- **OAuth complexity:** Requires Google Cloud setup
- **Content truncation:** 5000 character limit may cut off long newsletters
- **HTML parsing fragility:** Complex newsletters may lose structure
- **Single label:** Only fetches from "Newsletters" label

---

## Scoring Approach

### Algorithm Overview

The scoring system uses a **two-stage approach**:

#### Stage 1: Keyword Baseline (Always Used)

```
Final Score = min(1.0, depth_score + breadth_bonus + total_bonus)
```

**Components:**

1. **Depth Score (0.3 - 0.7):** Rewards multiple keywords matching within a single topic
   - 1 keyword = 0.3
   - 2 keywords = 0.4
   - 3 keywords = 0.5
   - 4 keywords = 0.6
   - 5+ keywords = 0.7

2. **Breadth Bonus (0.0 - 0.3):** Rewards matching across multiple topics
   - 1 topic = 0.0
   - 2 topics = 0.1
   - 3+ topics = 0.2 - 0.3

3. **Total Keyword Bonus (0.0 - 0.1):** Small bonus for high keyword density
   - 10+ total matches = 0.1 maximum

#### Stage 2: LLM Semantic Scoring (Optional)

- Only activated with `--use-llm` flag
- Applied only to top 30 candidates from Stage 1
- Uses Gemini Flash (free tier) for semantic relevance rating
- Falls back to keyword baseline if API fails

### Why This Approach

**Design Rationale:**

1. **Depth over breadth:** An article deeply covering one topic (e.g., 5 climate keywords) is more valuable than one barely touching 3 topics (1 keyword each). The original algorithm rewarded breadth equally, causing "topic blindness" where specialized content scored poorly.

2. **Free-first philosophy:** LLM scoring is expensive and slow. The keyword baseline provides 80% accuracy at 0% cost. LLM is reserved for edge cases or users who opt-in.

3. **Fast filtering:** The quick keyword check (`is_potentially_relevant()`) eliminates 90%+ of irrelevant content before any scoring, keeping processing time under 5 seconds.

4. **Configurable weights:** Topic weights in `interests.yaml` allow deprioritizing broad topics (AI Industry: 0.8) vs. specific interests (AI Filmmaking: 1.0).

### Benefits and Drawbacks

#### Benefits

| Benefit | Description |
|---------|-------------|
| **Speed** | Full pipeline runs in 2-5 seconds (keyword-only) |
| **Free** | No API costs unless LLM flag enabled |
| **Transparent** | Scoring formula is deterministic and explainable |
| **Configurable** | Add keywords/topics via YAML without code changes |
| **Depth-aware** | Specialized content now surfaces properly |

#### Drawbacks

| Drawback | Description |
|----------|-------------|
| **No semantic understanding** | "AI-powered video editing" won't match "Runway ML" without keyword |
| **Substring matching** | "AI" matches "painting" (false positive) |
| **No synonym handling** | "LLM" and "large language model" are separate keywords |
| **Static weights** | Can't learn from user behavior |
| **Limited context** | Only matches on title + summary, not full content |

### Potential Biases and Blind Spots

#### Bias: Keyword-Dense Content Favored

**Issue:** Articles that repeat keywords (listicles, SEO-optimized content) score higher than nuanced analysis that uses varied vocabulary.

**Example:** "Top 10 AI Video Tools: AI tools for AI video editing with AI" scores higher than "How Runway's new model is transforming post-production workflows."

**Impact:** Medium - may prioritize clickbait over substantive content.

#### Bias: English-Centric

**Issue:** All keywords are English. Non-English content or mixed-language content scores poorly.

**Impact:** Low for current use case (English sources), but limits international expansion.

#### Blind Spot: Emerging Topics

**Issue:** New topics not in keyword list are invisible. If a new AI filmmaking tool launches with a novel name, it won't match existing keywords.

**Example:** When "Sora" launched, it wouldn't match "AI video" keywords until manually added.

**Impact:** High - may miss breaking news on new tools/topics.

#### Blind Spot: Indirect Relevance

**Issue:** Articles about adjacent topics that don't use exact keywords are missed.

**Example:** An article about "Hollywood studios negotiating AI rights in contracts" is highly relevant to AI filmmaking but may not contain technical keywords.

**Impact:** Medium - misses industry/policy content.

#### Blind Spot: Video/Audio Content

**Issue:** YouTube and podcast content scored only on title/description, missing 95%+ of actual content.

**Example:** A 45-minute podcast episode discussing climate tech gets the same scoring as its 50-word show notes.

**Impact:** High - severely undervalues rich media content.

---

## Alternative Approaches

### Alternative 1: Embedding-Based Semantic Search

**Approach:** Convert all content and interest topics to vector embeddings, then score by cosine similarity.

**Implementation:**
- Use sentence-transformers (free, local) or OpenAI embeddings (paid)
- Embed each topic description once
- Embed each article title + content
- Score = max(cosine_similarity(article, topic) for topic in topics)

**Benefits:**
- Semantic understanding ("Runway ML" matches "AI video editing" concept)
- Handles synonyms automatically
- Better for nuanced content

**Drawbacks:**
- Slower (embedding generation takes 0.1-0.5s per item)
- Requires model download (500MB) or API costs
- Less explainable (why did this score 0.7?)
- May have unexpected biases from embedding model training

**Recommendation:** Consider as opt-in enhancement for users wanting better accuracy. Could run embeddings only on items that score 0.3-0.6 (borderline).

### Alternative 2: User Feedback Learning

**Approach:** Track user interactions (stars, clicks, time reading) and adjust scoring weights.

**Implementation:**
- Log all user actions with timestamps
- Calculate "engagement score" per source and topic
- Boost sources/topics with high engagement
- Demote sources/topics user ignores

**Benefits:**
- Personalizes to actual user preferences
- Self-correcting over time
- No keyword maintenance needed

**Drawbacks:**
- Cold start problem (no data initially)
- Requires significant usage to be effective
- May create filter bubbles
- Privacy considerations

**Recommendation:** The current stats tracking (`lib/stats.js`) already captures stars, clicks, and newsletter uses. This data could power a feedback loop in future versions.

### Alternative 3: Source-Based Pre-Filtering

**Approach:** Assign relevance tiers to sources rather than scoring individual items.

**Implementation:**
- Tier 1 (always show): Core sources like Curious Refuge, ComfyUI releases
- Tier 2 (score required): General tech news, needs keyword match
- Tier 3 (high threshold): Broad sources, needs strong match

**Benefits:**
- Faster (skip scoring for Tier 1)
- More predictable results
- Reduces noise from broad sources

**Drawbacks:**
- Less flexible
- New relevant content from Tier 3 sources may be missed
- Requires manual source classification

**Recommendation:** Could complement existing system. Sources with consistently high engagement could auto-promote to Tier 1.

### Alternative 4: LLM-Based Topic Extraction

**Approach:** Use LLM to extract topics from content, then match against user interests.

**Implementation:**
- For each article: "Extract the main topics from this article: [title + content]"
- Compare extracted topics to user's configured interests
- Score based on topic overlap

**Benefits:**
- Understands content semantically
- Can identify topics not in keyword list
- Handles new/emerging topics

**Drawbacks:**
- Expensive (API call per article)
- Slow (1-2 seconds per article)
- LLM may hallucinate topics
- Requires careful prompt engineering

**Recommendation:** Too expensive for current volume. Consider for "deep analysis" mode on starred/saved items.

---

## Recommendations

### Short-Term (Low Effort, High Impact)

1. **Add keyword synonyms:** Expand keywords to include common variations
   - "LLM" → also match "large language model"
   - "GenAI" → also match "generative AI"

2. **Improve substring matching:** Use word boundaries to prevent false positives
   - Current: "AI" matches "painting"
   - Better: Match "AI" only as whole word or start of compound

3. **Extract RSS categories:** Parse and log category tags from feeds to identify missing keywords

### Medium-Term (Moderate Effort)

4. **YouTube transcript extraction:** Add optional transcript fetching for video content
   - Use youtube-transcript-api library
   - Cache transcripts to avoid re-fetching
   - Only fetch for videos that pass initial relevance check

5. **Implement embedding-based fallback:** For items scoring 0.3-0.5, run embedding similarity as tiebreaker

6. **Source quality weighting:** Track click-through rates per source, boost high-engagement sources

### Long-Term (High Effort)

7. **User feedback loop:** Use starred items to refine keyword weights over time

8. **Full content extraction:** Follow article links to extract full text for better matching

9. **Podcast chapter detection:** Identify relevant segments within longer episodes

---

## Appendix: Current Configuration

### Configured Topics (6)

| Topic | Keywords | Weight |
|-------|----------|--------|
| AI Filmmaking & Video | 33 | 1.0 |
| AI Image Generation | 14 | 1.0 |
| Content Authenticity | 16 | 1.0 |
| Climate & Clean Energy | 20 | 1.0 |
| AI Industry & Models | 17 | 0.8 |
| Creative AI Tools | 10 | 0.7 |

### Configured Sources (67 total)

| Category | Count | Type |
|----------|-------|------|
| AI Labs & Research | 6 | RSS |
| AI Film & Video | 4 | RSS |
| Content Authenticity | 8 | RSS |
| Climate & Clean Energy | 10 | RSS |
| AI Podcasts | 5 | RSS |
| Climate Podcasts | 3 | RSS |
| YouTube Channels | 15 | RSS (via YouTube) |
| GitHub Releases | 7 | Atom |
| AI News & Commentary | 9 | RSS |

---

---

## Changelog

### January 2026 - Short-term Improvements Implemented

1. **Word boundary matching** - Keywords now use regex word boundaries to prevent false positives (e.g., "AI" no longer matches "painting")

2. **Expanded keyword synonyms** - Added ~50 new keyword variations including:
   - Tool variations (Runway ML, Pika Labs, Kling AI)
   - Technical terms (LoRA, ControlNet, inpainting)
   - Model names (SDXL, SD3, Flux.1)
   - Company variations (Google DeepMind, Meta AI)

3. **YouTube transcript extraction** - Added `youtube-transcript-api` integration:
   - Fetches auto-generated or manual captions (no API key required)
   - Falls back gracefully if library not installed
   - Transcripts appended to RSS content for richer keyword matching

4. **Podcast sparse-notes flagging** - Episodes with <100 words of show notes are flagged with `needs_review: true` for manual inspection

---

*Document generated: January 2026*
*Last updated: After short-term improvements implementation*