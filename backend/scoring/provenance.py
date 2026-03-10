import c2pa
import os
import requests
import tempfile
from pathlib import Path
from typing import Optional, List
from shared.base import ContentItem

class ProvenanceVerifier:
    def __init__(self):
        # The library is already initialized on import
        pass

    def verify(self, item: ContentItem) -> str:
        """
        Download media from item metadata, extract manifest data and verify integrity.
        Returns: Verified, Tampered, or Unknown
        """
        media_url = item.metadata.get('media_link')
        if not media_url:
            return "Unknown"

        tmp_path = None
        try:
            # Create a temporary file to store the downloaded media
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                response = requests.get(media_url, timeout=5)
                if response.status_code != 200:
                    return "Unknown"
                tmp.write(response.content)
                tmp_path = tmp.name

            try:
                # Use c2pa library to read manifest
                reader = c2pa.Reader(tmp_path)
                manifest_json = reader.json()

                if not manifest_json:
                    return "Unknown"

                # Check validation status
                # The validation array contains info about the integrity of the manifest
                validation_status = reader.validation()
                is_valid = all(v.get('status') == 'success' for v in validation_status)

                if is_valid:
                    return "Verified"
                else:
                    return "Tampered"

            except Exception as e:
                # If reading fails or validation is critical
                if "validation" in str(e).lower():
                    return "Tampered"
                return "Unknown"
        except Exception:
            return "Unknown"
        finally:
            # Cleanup temp file for all exit paths
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def process_batch(self, items: List[ContentItem]):
        for item in items:
            item.provenance_rating = self.verify(item)
