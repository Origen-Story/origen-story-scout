import time
from typing import List, Dict, Tuple
from ..llm.router import LLMRouter, TaskType
from ..sources.base import ContentItem
from ..config import settings


class Scorer:
    def __init__(self):
        self.router = LLMRouter()
        self.interests = settings.interests.topics

    def is_potentially_relevant(self, item: ContentItem) -> bool:
        """Fast keyword-based screening"""
        text = (item.title + " " + item.content).lower()
        for topic in self.interests:
            for kw in topic.keywords:
                if kw.lower() in text:
                    return True
        return False

    def _calculate_keyword_score(self, item: ContentItem) -> Tuple[float, Dict[str, int]]:
        """
        Calculate keyword score by counting ALL keyword matches.
        Returns (total_score, topic_hits) where topic_hits shows matches per topic.
        """
        text = (item.title + " " + item.content).lower()
        total_score = 0.0
        topic_hits = {}

        for topic in self.interests:
            hits = 0
            for kw in topic.keywords:
                # Count each keyword match (can match multiple times per topic)
                if kw.lower() in text:
                    hits += 1
                    total_score += topic.weight

            if hits > 0:
                topic_hits[topic.name] = hits

        return total_score, topic_hits

    def _get_keyword_baseline(self, item: ContentItem) -> float:
        """
        Calculate a normalized keyword-based score (0.0 to 1.0).
        More keyword hits = higher score.
        """
        score, topic_hits = self._calculate_keyword_score(item)
        num_topics_hit = len(topic_hits)
        total_keywords_hit = sum(topic_hits.values())

        # Scoring formula:
        # - Base: topics hit / total topics (0-1 range, how broad the match is)
        # - Boost: extra weight for multiple keyword hits within topics

        if num_topics_hit == 0:
            return 0.0

        # Breadth: what fraction of topics does this hit?
        breadth = num_topics_hit / len(self.interests)

        # Depth: average keywords per matched topic (capped at 3 for normalization)
        avg_hits_per_topic = min(3.0, total_keywords_hit / num_topics_hit)
        depth_bonus = (avg_hits_per_topic - 1) * 0.1  # 0-0.2 bonus for multiple hits

        # Combined score: breadth (0-1) + depth bonus (0-0.2), normalized to 0-1
        baseline = min(1.0, (breadth * 0.8) + depth_bonus + 0.1)

        return round(baseline, 3)

    def score_item(self, item: ContentItem) -> float:
        """
        Score an item using keyword matching + LLM semantic analysis.
        """
        # 1. Calculate keyword baseline
        keyword_baseline = self._get_keyword_baseline(item)

        if keyword_baseline == 0:
            return 0.0

        # 2. Semantic Scoring (LLM) - Only for items that passed keyword filter
        system_prompt = (
            "You are an expert analyst. Rate the relevance of the following article to these topics: "
            f"{[t.name for t in self.interests]}. Return EXACTLY a single float between 0.0 and 1.0."
        )
        prompt = f"Title: {item.title}\nContent Snippet: {item.content[:500]}"

        try:
            time.sleep(2)  # Rate limiting for free tier
            semantic_response = self.router.generate(
                prompt, task=TaskType.COMPLEX_LOGIC, system_prompt=system_prompt
            )
            semantic_score = float(semantic_response.strip())
        except Exception as e:
            # If LLM fails (rate limit), use the keyword baseline
            semantic_score = keyword_baseline
            if "quota" not in str(e).lower():
                print(f"Warning: Semantic scoring fallback used for '{item.title[:50]}...'")

        # 3. Provenance Weighting
        provenance_multiplier = 1.0
        if item.provenance_rating == "Verified":
            provenance_multiplier = 1.2
        elif item.provenance_rating == "Tampered":
            provenance_multiplier = 0.5

        final_score = semantic_score * provenance_multiplier
        return round(min(final_score, 1.0), 2)

    def rank_items(self, items: List[ContentItem]) -> List[ContentItem]:
        """
        Rank items by relevance. Uses fast keyword scoring to select candidates,
        then LLM scoring for top candidates.
        """
        # Fast sorting by keyword score first to pick top candidates
        items_with_scores = [
            (item, self._get_keyword_baseline(item)) for item in items
        ]
        items_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Only do expensive semantic scoring for top 30 items
        top_candidates = [item for item, score in items_with_scores[:30]]

        for item in top_candidates:
            item.relevance_score = self.score_item(item)

        # Filter and Sort
        min_score = settings.interests.preferences.min_relevance_score
        filtered = [i for i in top_candidates if i.relevance_score >= min_score]
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)

        return filtered
