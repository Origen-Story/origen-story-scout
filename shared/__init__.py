"""
Shared Module

Common data types and configuration used across backend modules:
- config.py: Application configuration and settings
- base.py: ContentItem dataclass and ContentSource base class
- report.py: Report generation and JSON output
- storage/: Archive and persistence utilities
"""

from .config import settings, Config, Topic, UserPreferences, InterestConfig
from .base import ContentItem, ContentSource

__all__ = [
    'settings', 'Config', 'Topic', 'UserPreferences', 'InterestConfig',
    'ContentItem', 'ContentSource'
]
