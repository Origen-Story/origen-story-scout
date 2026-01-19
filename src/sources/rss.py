import feedparser
from datetime import datetime
from typing import List
import time
from .base import ContentItem, ContentSource
from ..config import settings

class RSSSource(ContentSource):
    def __init__(self, feeds=None):
        self.feeds = feeds or settings.sources.rss_feeds

    def fetch(self) -> List[ContentItem]:
        all_items = []
        import socket
        # Set a global timeout for socket operations used by feedparser
        socket.setdefaulttimeout(20.0)

        for feed_config in self.feeds:
            try:
                print(f"Fetching: {feed_config.name}...")
                feed = feedparser.parse(feed_config.url)
                if feed.get('bozo', 0) == 1 and not feed.entries:
                    print(f"Warning: Potential issue with feed {feed_config.name}")
                    continue
            except Exception as e:
                print(f"Error fetching {feed_config.name}: {e}")
                continue
            
            for entry in feed.entries:
                # Skip entries without a link (required field)
                entry_link = entry.get('link') or entry.get('id')
                if not entry_link:
                    continue

                # Handle different date formats in RSS/Atom
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    except (TypeError, ValueError):
                        published = datetime.now()
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    try:
                        published = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                    except (TypeError, ValueError):
                        published = datetime.now()
                else:
                    published = datetime.now()

                # Basic filtering by time window (default 7 days)
                days_delta = (datetime.now() - published).days
                if days_delta > settings.interests.preferences.time_window_days:
                    continue

                # Extract media link if available
                media_link = None
                if 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', '') or link.get('rel') == 'enclosure':
                            media_link = link.get('href')
                            break

                if not media_link and 'media_content' in entry:
                    # Some feeds use media:content
                    media_link = entry.media_content[0].get('url')

                item = ContentItem(
                    id=entry.get('id', entry_link),
                    title=entry.get('title', 'No Title'),
                    content=entry.get('summary', entry.get('description', '')),
                    url=entry_link,
                    source_name=feed_config.name,
                    source_category=feed_config.category,
                    published_date=published,
                    author=entry.get('author'),
                    metadata={'media_link': media_link}
                )
                all_items.append(item)
                
        return all_items
