"""
Scoring Module

Content relevance and quality assessment:
- scorer.py: Keyword-based relevance scoring
- trending.py: Cross-source trending detection
- provenance.py: C2PA content authenticity verification
"""

from .scorer import Scorer
from .trending import detect_trending, apply_trending_boost
from .provenance import ProvenanceVerifier

__all__ = ['Scorer', 'detect_trending', 'apply_trending_boost', 'ProvenanceVerifier']
