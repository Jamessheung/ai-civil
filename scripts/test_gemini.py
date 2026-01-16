import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.services.evidence_extractor import EvidenceExtractor
from backend.models import RawItem, Source
from datetime import datetime
# Mock classes to bypass SQLAlchemy
class MockSession:
    def __init__(self):
        self.mock_item = None
        
    def query(self, model):
        return self
        
    def filter(self, condition):
        return self
        
    def first(self):
        return self.mock_item

    def add(self, obj):
        print(f"   [MockDB] Added object: {obj}")

    def commit(self):
        print("   [MockDB] Commit called")

from types import SimpleNamespace

def test_gemini_integration():
    # Use Mock DB
    db = MockSession()
    
    print("🧪 Creating Test RawItem (Plain Mock)...")
    # Use SimpleNamespace to avoid SQLAlchemy instrumentation
    mock_item = SimpleNamespace(
        source_id=1,
        title="Leaked Memo: Quantum GPU Breakthrough",
        content="Internal sources at NVIDIA suggest a 500x leap in quantum processing is imminent. While the CEO has denied immediate consumer availability, leaked lab notes indicate 'Project Q' is already operational. This could destabilize the entire crypto market overnight.",
        url="http://leak-news.test/crypto-q",
        fetched_at=datetime.now(),
        content_hash="hash_test_gemini_1",
        item_id=999,
        # Mock nested source
        source=SimpleNamespace(source_type='official'),
        canonical_url=None
    )
    
    # Inject into mock DB
    db.mock_item = mock_item
    
    print(f"🚀 invoking EvidenceExtractor (Gemini Check: {bool(os.getenv('GEMINI_API_KEY'))})...")
    
    # Debug: List Models
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    print("📋 Available Models:")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"   - {m.name}")
    except Exception as e:
        print(f"   (List failed: {e})")

    extractor = EvidenceExtractor(db)
    evidence_list = extractor.process_item(999)
    
    print("\n✅ Extraction Result:")
    for ev in evidence_list:
        print(f"--------------------------------------------------")
        print(f"Level: L{ev.level} ({ev.evidence_kind})")
        print(f"Reliability: {ev.reliability_score}")
        print(f"Extract: {ev.extract}")
        print(f"Pointer: {ev.pointer}")
        print(f"--------------------------------------------------")

    # cleanup
    # db.delete(mock_item)
    # db.commit()

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not found in env. Logic will use KEYWORDS fallback.")
    test_gemini_integration()
