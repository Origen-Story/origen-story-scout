"""
Ingestion Module

Content source fetchers for various platforms:
- rss.py: RSS/Atom feed fetching
- gmail.py: Gmail newsletter fetching
- youtube.py: YouTube transcript extraction
"""

from shared.base import ContentItem, ContentSource
from .rss import RSSSource

__all__ = ['ContentItem', 'ContentSource', 'RSSSource']
