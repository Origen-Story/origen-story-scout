"""
Trending detection module - identifies stories covered by multiple sources.

Cross-source coverage is a strong signal of story importance:
- Same story from 3+ sources = high trending signal
- Uses fuzzy title matching to group similar stories
- Boosts relevance scores for trending items
"""

from collections import defaultdict
from difflib import SequenceMatcher
from ..sources.base import ContentItem


def similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def extract_key_terms(title: str) -> set:
    """Extract significant terms from a title for comparison."""
    # Common words to ignore
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as',
        'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'under', 'again', 'further', 'then', 'once', 'here',
        'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
        'because', 'until', 'while', 'about', 'against', 'this', 'that',
        'these', 'those', 'what', 'which', 'who', 'whom', 'its', 'it', 'new',
        'says', 'said', 'report', 'reports', 'according', 'announces', 'launches'
    }

    # Extract words, filter stopwords and short words
    words = set()
    for word in title.lower().split():
        # Remove punctuation
        clean = ''.join(c for c in word if c.isalnum())
        if clean and len(clean) > 2 and clean not in stopwords:
            words.add(clean)

    return words


def are_similar_stories(item1: ContentItem, item2: ContentItem, threshold: float = 0.5) -> bool:
    """
    Determine if two items are about the same story.
    Uses both title similarity and key term overlap.
    """
    # Quick check: exact title match
    if item1.title.lower() == item2.title.lower():
        return True

    # Check title similarity
    title_sim = similarity(item1.title, item2.title)
    if title_sim > 0.7:
        return True

    # Check key term overlap
    terms1 = extract_key_terms(item1.title)
    terms2 = extract_key_terms(item2.title)

    if not terms1 or not terms2:
        return False

    # Calculate Jaccard similarity of key terms
    intersection = terms1 & terms2
    union = terms1 | terms2
    term_overlap = len(intersection) / len(union) if union else 0

    # If significant term overlap AND some title similarity, consider same story
    if term_overlap >= threshold and title_sim > 0.3:
        return True

    # Check for shared proper nouns (company names, product names)
    # These are typically capitalized words
    def get_proper_nouns(title):
        words = title.split()
        return {w.lower() for w in words if w[0].isupper() and len(w) > 2}

    proper1 = get_proper_nouns(item1.title)
    proper2 = get_proper_nouns(item2.title)
    shared_proper = proper1 & proper2

    # If 2+ shared proper nouns, likely same story
    if len(shared_proper) >= 2:
        return True

    return False


def detect_trending(items: list[ContentItem], min_sources: int = 2) -> dict:
    """
    Detect trending stories by finding items covered by multiple sources.

    Returns:
        dict with:
        - 'clusters': list of story clusters (each cluster is a list of related items)
        - 'trending_ids': set of item IDs that are part of trending clusters
        - 'boost_map': dict mapping item_id -> trending boost factor
    """
    if not items:
        return {'clusters': [], 'trending_ids': set(), 'boost_map': {}}

    # Group items by source to ensure we're counting cross-source coverage
    items_by_source = defaultdict(list)
    for item in items:
        items_by_source[item.source_name].append(item)

    # Build clusters of similar stories
    clusters = []
    assigned = set()

    for i, item in enumerate(items):
        if item.id in assigned:
            continue

        # Start a new cluster with this item
        cluster = [item]
        cluster_sources = {item.source_name}
        assigned.add(item.id)

        # Find all similar items from OTHER sources
        for j, other in enumerate(items):
            if other.id in assigned:
                continue
            if other.source_name in cluster_sources:
                # Skip items from same source (we want cross-source)
                continue

            # Check if similar to any item in cluster
            for cluster_item in cluster:
                if are_similar_stories(cluster_item, other):
                    cluster.append(other)
                    cluster_sources.add(other.source_name)
                    assigned.add(other.id)
                    break

        # Only keep clusters with multiple sources
        if len(cluster_sources) >= min_sources:
            clusters.append({
                'items': cluster,
                'sources': list(cluster_sources),
                'source_count': len(cluster_sources),
                'representative_title': cluster[0].title
            })

    # Sort clusters by source count (most covered first)
    clusters.sort(key=lambda c: c['source_count'], reverse=True)

    # Build trending IDs and boost map
    trending_ids = set()
    boost_map = {}

    for cluster in clusters:
        source_count = cluster['source_count']
        # Boost factor: 2 sources = 1.1x, 3 sources = 1.2x, etc.
        boost = 1.0 + (source_count - 1) * 0.1

        for item in cluster['items']:
            trending_ids.add(item.id)
            boost_map[item.id] = boost

    return {
        'clusters': clusters,
        'trending_ids': trending_ids,
        'boost_map': boost_map
    }


def apply_trending_boost(items: list[ContentItem], boost_map: dict) -> None:
    """Apply trending boost to item relevance scores in-place."""
    for item in items:
        if item.id in boost_map:
            boost = boost_map[item.id]
            old_score = item.relevance_score or 0
            item.relevance_score = min(1.0, old_score * boost)
            item.metadata = item.metadata or {}
            item.metadata['trending'] = True
            item.metadata['trending_boost'] = boost
