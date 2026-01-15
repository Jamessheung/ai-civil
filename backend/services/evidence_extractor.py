from sqlalchemy.orm import Session
from ..models import RawItem, Evidence, Source
import json
import re

class EvidenceExtractor:
    def __init__(self, db: Session):
        self.db = db

    def process_item(self, raw_item_id: int):
        """Extract evidence from a raw item using rules."""
        item = self.db.query(RawItem).filter(RawItem.item_id == raw_item_id).first()
        if not item:
            return []

        # Simple rule-based extraction
        # In reality, this would be an LLM or complex NLP pipeline
        # Here we simulate the L5-L1 logic with keywords
        
        sentences = re.split(r'(?<=[.!?])\s+', item.content)
        extracted_evidence = []

        is_official_source = item.source.source_type == 'official'
        
        for idx, sent in enumerate(sentences):
            if len(sent) < 20: continue # Skip short fragments

            level = 3 # Default: Weak Secondary
            kind = 'fact'
            
            # Logic: Determine Level
            lower_sent = sent.lower()

            # L1: Inference / Speculation
            if any(w in lower_sent for w in ['predicts', 'might', 'speculates', 'could be', 'rumor']):
                level = 1
                kind = 'inference'
            
            # L2: Social / Noise
            elif 'twitter' in item.url or 'weibo' in item.url:
                level = 2
            
            # L5: Official (Overrides L3)
            elif is_official_source or 'official statement' in lower_sent or 'financial report' in lower_sent:
                level = 5
                kind = 'fact'
            
            # L4: Strong Secondary (Direct References)
            elif 'according to document' in lower_sent or 'dataset' in lower_sent:
                level = 4
                kind = 'data' if 'dataset' in lower_sent else 'quote'

            # Pointer Struct
            pointer = {
                "url": item.canonical_url or item.url,
                "match_text": sent[:50] + "...", # Simplified match text
                "source_hash": item.content_hash,
                "captured_at": item.fetched_at.isoformat() if item.fetched_at else None
            }

            # Create Evidence object (not committed yet, let caller handle)
            evidence = Evidence(
                raw_item_id=item.item_id,
                cluster_id=None, # To be assigned by Clusterer
                level=level,
                extract=sent,
                pointer=pointer,
                reliability_score=0.9 if level >=4 else 0.6,
                evidence_kind=kind
            )
            extracted_evidence.append(evidence)
            self.db.add(evidence)
        
        self.db.commit()
        return extracted_evidence
