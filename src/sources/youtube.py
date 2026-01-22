"""
YouTube transcript extraction utilities.

Uses youtube-transcript-api to fetch auto-generated or manual captions.
No API key required - scrapes directly from YouTube's caption system.
"""

import re
from typing import Optional

# Try to import youtube-transcript-api, gracefully handle if not installed
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
    )
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    YouTubeTranscriptApi = None
    TranscriptsDisabled = Exception
    NoTranscriptFound = Exception
    VideoUnavailable = Exception


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats.

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def fetch_transcript(video_id: str, max_chars: int = 5000) -> Optional[str]:
    """
    Fetch transcript for a YouTube video.

    Args:
        video_id: The YouTube video ID (11 characters)
        max_chars: Maximum characters to return (default 5000)

    Returns:
        Transcript text or None if unavailable
    """
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        return None

    try:
        # Try to get English transcript first, fall back to any available
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer manually created English transcript
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except NoTranscriptFound:
            # Fall back to auto-generated English
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except NoTranscriptFound:
                # Fall back to any available transcript
                try:
                    transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                except NoTranscriptFound:
                    return None

        # Fetch the actual transcript data
        transcript_data = transcript.fetch()

        # Combine all text segments
        full_text = ' '.join(segment['text'] for segment in transcript_data)

        # Clean up common transcript artifacts
        full_text = full_text.replace('\n', ' ')
        full_text = re.sub(r'\s+', ' ', full_text)  # Normalize whitespace
        full_text = full_text.strip()

        # Truncate if needed
        if len(full_text) > max_chars:
            # Try to cut at a sentence boundary
            truncated = full_text[:max_chars]
            last_period = truncated.rfind('.')
            if last_period > max_chars * 0.8:  # Only if we're not losing too much
                truncated = truncated[:last_period + 1]
            full_text = truncated + '...'

        return full_text

    except TranscriptsDisabled:
        # Video has transcripts disabled
        return None
    except VideoUnavailable:
        # Video doesn't exist or is private
        return None
    except Exception as e:
        # Log but don't crash on unexpected errors
        print(f"Warning: Could not fetch transcript for {video_id}: {e}")
        return None


def fetch_transcript_from_url(url: str, max_chars: int = 5000) -> Optional[str]:
    """
    Fetch transcript from a YouTube URL.

    Convenience wrapper that extracts video ID and fetches transcript.
    """
    if not YOUTUBE_TRANSCRIPT_AVAILABLE:
        return None

    video_id = extract_video_id(url)
    if not video_id:
        return None

    return fetch_transcript(video_id, max_chars)
