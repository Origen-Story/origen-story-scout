import json
import hashlib
from pathlib import Path
from ..llm.router import LLMRouter, TaskType
from ..sources.base import ContentItem
from typing import List


class SummaryCache:
    """Cache for summaries to avoid re-processing the same content."""

    def __init__(self, cache_path: str = "data/summaries_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)

    def _get_content_hash(self, item: ContentItem) -> str:
        """Generate a hash based on content to detect duplicates."""
        content = f"{item.title}|{item.content or ''}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, item: ContentItem) -> str | None:
        """Get cached summary if available."""
        content_hash = self._get_content_hash(item)
        return self._cache.get(content_hash)

    def set(self, item: ContentItem, summary: str):
        """Cache a summary."""
        content_hash = self._get_content_hash(item)
        self._cache[content_hash] = summary
        self._save_cache()


class Summarizer:
    def __init__(self):
        self.router = LLMRouter()
        self.cache = SummaryCache()

    def summarize_item(self, item: ContentItem) -> str:
        # Check cache first
        cached = self.cache.get(item)
        if cached:
            print(f"  [CACHED] Using cached summary for: {item.title[:50]}...")
            return cached

        system_prompt = (
            "You are a professional content curator. Write a single concise summary of the article in 1-2 sentences (max 500 characters). "
            "Focus on what the article is about and why it matters. "
            "Do NOT include any preamble like 'Here's a summary' or 'This article discusses'. Just state the facts directly."
        )
        # Truncate content to avoid hitting TPM limit on free tier
        truncated_content = item.content[:2000] if item.content else "No content available."
        prompt = f"Title: {item.title}\nSource: {item.source_name}\n\nContent:\n{truncated_content}"

        try:
            import time
            time.sleep(5) # Rate limiting for free tier
            # We use general task for basic summarization
            summary = self.router.generate(prompt, task=TaskType.GENERAL, system_prompt=system_prompt)
            # Cache the result
            self.cache.set(item, summary)
            return summary
        except Exception as e:
            print(f"Warning: Failed to summarize '{item.title}': {e}")
            return "Summary unavailable."

    def process_batch(self, items: List[ContentItem]):
        for item in items:
            item.summary = self.summarize_item(item)
