"""
Storage Module

Data persistence and archive management:
- archive.py: Processed item tracking to avoid reprocessing
"""

from .archive import Archive

__all__ = ['Archive']
