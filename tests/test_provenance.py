import pytest
from shared.base import ContentItem
from backend.scoring.provenance import ProvenanceVerifier
from datetime import datetime

def test_provenance_unknown_without_media():
    verifier = ProvenanceVerifier()
    item = ContentItem(
        id="1", title="Test", content="Body", url="http://ex.com",
        source_name="Src", source_category="Cat", published_date=datetime.now(),
        metadata={}
    )
    assert verifier.verify(item) == "Unknown"

def test_provenance_handles_missing_media_gracefully():
    verifier = ProvenanceVerifier()
    item = ContentItem(
        id="1", title="Test", content="Body", url="http://ex.com",
        source_name="Src", source_category="Cat", published_date=datetime.now(),
        metadata={'media_link': 'http://invalid.url/image.jpg'}
    )
    # Should return Unknown on download error
    assert verifier.verify(item) == "Unknown"
