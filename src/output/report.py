import json
from pathlib import Path
from typing import List
from ..sources.base import ContentItem
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir: str = "dashboard/public/data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(self, items: List[ContentItem], filename: str = "latest_report.json"):
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_relevant": len(items),
            "stories": [
                {
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "url": item.url,
                    "source_name": item.source_name,
                    "source_category": item.source_category,
                    "published_date": item.published_date.isoformat(),
                    "author": item.author,
                    "relevance_score": item.relevance_score,
                    "provenance_rating": item.provenance_rating,
                    "summary": item.summary,
                    "media_link": item.metadata.get('media_link')
                }
                for item in items
            ]
        }
        
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_path
