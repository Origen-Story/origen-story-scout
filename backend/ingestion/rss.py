import feedparser
from datetime import datetime
from typing import List
import time
from shared.base import ContentItem, ContentSource
from shared.config import settings
from .youtube import fetch_transcript_from_url, YOUTUBE_TRANSCRIPT_AVAILABLE

class RSSSource(ContentSource):
    def __init__(self, feeds=None):
        self.feeds = feeds or settings.sources.rss_feeds
        self._transcript_warning_shown = False

    def fetch(self) -> List[ContentItem]:
        all_items = []
        import socket
        # Set a global timeout for socket operations used by feedparser
        socket.setdefaulttimeout(20.0)

        # Show one-time warning if transcript extraction is unavailable
        if not YOUTUBE_TRANSCRIPT_AVAILABLE and not self._transcript_warning_shown:
            print("Note: youtube-transcript-api not installed. YouTube transcripts will not be fetched.")
            print("      Install with: pip install youtube-transcript-api")
            self._transcript_warning_shown = True

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
                # Get link and ID separately - ID might not be a valid URL
                entry_link = entry.get('link')
                entry_id = entry.get('id') or entry_link

                # For URL, only use link if it looks like a URL, otherwise try to find one
                if not entry_link or not entry_link.startswith(('http://', 'https://')):
                    # Try to find a URL in the entry's links list
                    for link in entry.get('links', []):
                        href = link.get('href', '')
                        if href.startswith(('http://', 'https://')):
                            entry_link = href
                            break

                # Skip entries without a valid URL
                if not entry_link or not entry_link.startswith(('http://', 'https://')):
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

                # Get base content from RSS
                base_content = entry.get('summary', entry.get('description', ''))

                # For YouTube videos, try to fetch transcript for richer content
                is_youtube = feed_config.category == 'AI YouTube' or 'youtube.com' in entry_link
                transcript = None
                if is_youtube:
                    transcript = fetch_transcript_from_url(entry_link)

                # Use transcript if available, otherwise fall back to RSS description
                if transcript:
                    # Combine RSS description with transcript for full context
                    content = f"{base_content}\n\n[Transcript]\n{transcript}"
                else:
                    content = base_content

                # Check if this is a podcast with sparse show notes
                is_podcast = 'podcast' in feed_config.category.lower()
                content_word_count = len(content.split())
                needs_review = False

                if is_podcast and content_word_count < 100:
                    # Flag podcasts with less than 100 words of show notes
                    needs_review = True

                item = ContentItem(
                    id=entry_id,
                    title=entry.get('title', 'No Title'),
                    content=content,
                    url=entry_link,
                    source_name=feed_config.name,
                    source_category=feed_config.category,
                    published_date=published,
                    author=entry.get('author'),
                    needs_review=needs_review,
                    metadata={
                        'media_link': media_link,
                        'has_transcript': transcript is not None,
                        'is_youtube': is_youtube,
                        'is_podcast': is_podcast,
                        'content_word_count': content_word_count,
                    }
                )
                all_items.append(item)
                
        return all_items
