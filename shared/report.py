import json
import re
from pathlib import Path
from typing import List
from collections import Counter
from .base import ContentItem
from .config import settings
from datetime import datetime


# Common words to ignore when extracting trending terms
STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'to', 'of',
    'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'between', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while',
    'about', 'against', 'this', 'that', 'these', 'those', 'what', 'which',
    'who', 'whom', 'its', 'it', 'new', 'says', 'said', 'report', 'reports',
    'according', 'year', 'years', 'day', 'days', 'time', 'now', 'also',
    'like', 'just', 'even', 'back', 'after', 'over', 'such', 'our', 'out',
    'use', 'your', 'way', 'many', 'made', 'make', 'first', 'get', 'using',
    'read', 'more', 'one', 'two', 'three', 'their', 'you', 'they', 'we',
    'been', 'its', 'than', 'any', 'news', 'latest', 'today', 'week',
    'month', 'click', 'here', 'view', 'sign', 'email', 'newsletter',
    'subscribe', 'unsubscribe', 'sponsor', 'sponsored', 'advertisement',
    # Too generic for trending
    'ai', 'tech', 'data', 'code', 'world', 'company', 'companies', 'us',
    'uk', 'january', 'february', 'march', 'april', 'may', 'june', 'july',
    'august', 'september', 'october', 'november', 'december', 'monday',
    'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    # Common article phrases
    'honest', 'an honest', 'biased', 'review', 'breaking', 'exclusive',
    'update', 'latest', 'welcome', 'hello', 'good', 'best', 'top',
    'things', 'stuff', 'part', 'episode', 'issue', 'edition',
    'image', 'generator', 'non', 'via', 'full', 'free', 'paid', 'premium',
    'note', 'notes', 'affiliate', 'affiliated', 'not affiliated', 'please',
    'thank', 'thanks', 'learn', 'discover', 'find', 'see', 'check', 'watch',
    'video', 'article', 'post', 'blog', 'story', 'stories'
}


# High-value terms to always look for (case-insensitive)
KNOWN_ENTITIES = {
    # Companies
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'google': 'Google',
    'microsoft': 'Microsoft',
    'meta': 'Meta',
    'nvidia': 'Nvidia',
    'apple': 'Apple',
    'amazon': 'Amazon',
    'deepmind': 'DeepMind',
    'mistral': 'Mistral',
    'stability': 'Stability AI',
    'runway': 'Runway',
    'midjourney': 'Midjourney',
    'hugging face': 'Hugging Face',
    'huggingface': 'Hugging Face',
    # Products/Models
    'chatgpt': 'ChatGPT',
    'gpt-4': 'GPT-4',
    'gpt-5': 'GPT-5',
    'gpt 4': 'GPT-4',
    'gpt 5': 'GPT-5',
    'claude': 'Claude',
    'claude code': 'Claude Code',
    'gemini': 'Gemini',
    'grok': 'Grok',
    'copilot': 'Copilot',
    'sora': 'Sora',
    'dall-e': 'DALL-E',
    'dalle': 'DALL-E',
    'stable diffusion': 'Stable Diffusion',
    'flux': 'Flux',
    'comfyui': 'ComfyUI',
    'llama': 'Llama',
    'mistral': 'Mistral',
    # People
    'sam altman': 'Sam Altman',
    'elon musk': 'Elon Musk',
    'dario amodei': 'Dario Amodei',
    'satya nadella': 'Satya Nadella',
    # Concepts
    'agi': 'AGI',
    'llm': 'LLM',
}


def extract_trending_terms(items: List[ContentItem], min_mentions: int = 2, max_terms: int = 8) -> List[dict]:
    """
    Extract specific terms/entities that appear across multiple stories.
    Focuses on proper nouns, product names, company names, and specific topics.
    Returns list of {term, count, sources} sorted by count descending.
    Count = total number of articles mentioning the term (not unique sources).
    """
    # Track terms: article count and which sources mention them
    term_data = {}  # normalized term -> {"articles": [], "sources": set()}

    for item in items:
        text = f"{item.title} {item.content or ''}"
        text_lower = text.lower()

        found_terms = set()

        # 1. Check for known entities (case-insensitive)
        for pattern, display_name in KNOWN_ENTITIES.items():
            if pattern in text_lower:
                found_terms.add(display_name)

        # 2. Find capitalized words (likely proper nouns)
        caps_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for match in re.findall(caps_pattern, text):
            term = match.strip()
            term_lower = term.lower()
            # Skip if any word in the term is a stopword
            term_words = term_lower.split()
            if any(w in STOPWORDS for w in term_words):
                continue
            if len(term) > 2 and term_lower not in STOPWORDS:
                # Skip if it's already captured by known entities
                if term_lower not in KNOWN_ENTITIES:
                    found_terms.add(term)

        # 3. Find tech/product terms (all caps or camelCase)
        tech_pattern = r'\b([A-Z]{2,}(?:-[A-Z0-9]+)?|[A-Z][a-z]+[A-Z][a-zA-Z]*)\b'
        for match in re.findall(tech_pattern, text):
            if len(match) > 1 and match.lower() not in STOPWORDS:
                if match.lower() not in KNOWN_ENTITIES:
                    found_terms.add(match)

        # 4. Find version numbers (e.g., GPT-4, V7, Gen-3)
        version_pattern = r'\b([A-Za-z]+[-\s]?[0-9]+(?:\.[0-9]+)?)\b'
        for match in re.findall(version_pattern, text):
            if len(match) > 2:
                found_terms.add(match)

        # Add terms to tracking
        for term in found_terms:
            normalized = term.strip()
            if normalized not in term_data:
                term_data[normalized] = {"articles": [], "sources": set()}
            term_data[normalized]["articles"].append(item.id)
            term_data[normalized]["sources"].add(item.source_name)

    # Filter to terms mentioned in multiple articles
    trending = []
    for term, data in term_data.items():
        article_count = len(data["articles"])
        if article_count >= min_mentions:
            trending.append({
                "term": term,
                "count": article_count,  # Total articles, not unique sources
                "sources": list(data["sources"])[:5]  # Keep sources for tooltip
            })

    # Sort by count descending, then alphabetically
    trending.sort(key=lambda x: (-x["count"], x["term"]))

    return trending[:max_terms]


class ReportGenerator:
    def __init__(self, output_dir: str = "frontend/public/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(self, items: List[ContentItem], filename: str = "latest_report.json", trending_clusters: list = None, all_items: List[ContentItem] = None):
        # Use all_items for statistics if provided, otherwise use items
        stats_items = all_items if all_items else items

        # Extract trending terms from all items (for better coverage)
        trending_terms = extract_trending_terms(stats_items, min_mentions=2, max_terms=10)

        # Count trending stories (cross-source coverage)
        trending_count = sum(1 for item in items if item.metadata and item.metadata.get('trending'))

        # Format cross-source story clusters for the dashboard
        cross_source_stories = []
        if trending_clusters:
            for cluster in trending_clusters:
                cross_source_stories.append({
                    "topic": cluster['representative_title'],
                    "source_count": cluster['source_count'],
                    "sources": cluster['sources'],
                    "story_ids": [item.id for item in cluster['items']]
                })

        # Count by source type (Newsletter, YouTube, RSS) from ALL items
        source_type_counts = {}
        for item in stats_items:
            category = item.source_category if item.source_category else "Unknown"
            # Determine display type based on category
            if category == "Newsletter":
                display_type = "Newsletter"
            elif category == "AI YouTube":
                display_type = "YouTube"
            elif category == "GitHub Releases":
                display_type = "GitHub"
            elif "Podcast" in category:
                display_type = "Podcast"
            else:
                display_type = "RSS"
            source_type_counts[display_type] = source_type_counts.get(display_type, 0) + 1

        # Track detailed categories from ALL items
        category_counts = {}
        for item in stats_items:
            cat = item.source_category if item.source_category else "Unknown"
            category_counts[cat] = category_counts.get(cat, 0) + 1

        def serialize_item(item):
            return {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "url": item.url,
                "source_name": item.source_name,
                "source_category": item.source_category,
                "published_date": item.published_date.isoformat(),
                "author": item.author,
                "relevance_score": item.relevance_score,
                "provenance_rating": item.provenance_rating,
                "summary": item.summary,
                "media_link": item.metadata.get('media_link') if item.metadata else None,
                "trending": item.metadata.get('trending', False) if item.metadata else False,
                "trending_boost": item.metadata.get('trending_boost') if item.metadata else None,
                # New fields for enhanced content
                "needs_review": getattr(item, 'needs_review', False),
                "has_transcript": item.metadata.get('has_transcript', False) if item.metadata else False,
                "is_youtube": item.metadata.get('is_youtube', False) if item.metadata else False,
                "is_podcast": item.metadata.get('is_podcast', False) if item.metadata else False,
                "content_word_count": item.metadata.get('content_word_count') if item.metadata else None,
            }

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_relevant": len(stats_items),
            "top_stories_count": len(items),
            "trending_count": trending_count,
            "trending_terms": trending_terms,
            "cross_source_stories": cross_source_stories,
            "source_breakdown": source_type_counts,
            "category_breakdown": category_counts,
            # Top 30 stories for main grid/list view
            "stories": [serialize_item(item) for item in items],
            # All scored stories for "All Stories" view
            "all_stories": [serialize_item(item) for item in stats_items] if all_items else None
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path
