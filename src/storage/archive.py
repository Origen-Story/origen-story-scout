import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Set, Dict, Any, List
from ..sources.base import ContentItem

class Archive:
    def __init__(self, storage_path: str = "data/archive.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load archive data including timestamps"""
        if not self.storage_path.exists():
            return {'items': {}}
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                # Migrate old format (list of IDs) to new format (dict with timestamps)
                if 'processed_ids' in data and 'items' not in data:
                    items = {}
                    for item_id in data['processed_ids']:
                        items[item_id] = {'added_at': datetime.now().isoformat()}
                    return {'items': items}
                return data
        except (json.JSONDecodeError, IOError):
            return {'items': {}}

    @property
    def processed_ids(self) -> Set[str]:
        return set(self._data.get('items', {}).keys())

    def is_processed(self, item_id: str) -> bool:
        return item_id in self._data.get('items', {})

    def mark_processed(self, item: ContentItem):
        """Mark an item as processed with timestamp"""
        if 'items' not in self._data:
            self._data['items'] = {}
        self._data['items'][item.id] = {
            'added_at': datetime.now().isoformat(),
            'published_date': item.published_date.isoformat() if item.published_date else None
        }
        self._save()

    def prune_old_items(self, days: int = 10):
        """Remove items older than specified days from archive"""
        if 'items' not in self._data:
            return

        cutoff = datetime.now() - timedelta(days=days)
        items_to_remove = []

        for item_id, item_data in self._data['items'].items():
            # Check published_date first, fall back to added_at
            date_str = item_data.get('published_date') or item_data.get('added_at')
            if date_str:
                try:
                    item_date = datetime.fromisoformat(date_str)
                    if item_date < cutoff:
                        items_to_remove.append(item_id)
                except (ValueError, TypeError):
                    continue

        if items_to_remove:
            for item_id in items_to_remove:
                del self._data['items'][item_id]
            self._save()
            print(f"Pruned {len(items_to_remove)} old items from archive")

    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self._data, f, indent=2)

    def filter_new(self, items: List[ContentItem]) -> List[ContentItem]:
        return [item for item in items if not self.is_processed(item.id)]
