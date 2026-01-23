"""
Summarizer Module

LLM-based content summarization:
- summarizer.py: Main summarization orchestration
- base.py: Base LLM interface
- gemini.py: Google Gemini integration
- claude.py: Anthropic Claude integration
- router.py: LLM routing logic
"""

from .summarizer import Summarizer

__all__ = ['Summarizer']
