from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class ContentItem:
    id: str
    title: str
    content: str
    url: str
    source_name: str
    source_category: str
    published_date: datetime
    author: Optional[str] = None
    summary: Optional[str] = None
    relevance_score: float = 0.0
    provenance_rating: str = "Unknown"  # Verified, Tampered, Unknown
    needs_review: bool = False  # Flag for items needing manual review (e.g., sparse podcast notes)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContentSource:
    def fetch(self) -> List[ContentItem]:
        raise NotImplementedError("Subclasses must implement fetch()")
