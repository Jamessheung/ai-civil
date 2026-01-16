from sqlalchemy.orm import Session
from ..models import RawItem, Evidence, Source
import json
import re
import os

class EvidenceExtractor:
    def __init__(self, db: Session):
        self.db = db

    def process_item(self, raw_item_id: int):
        """Extract evidence from a raw item using Gemini AI (with keyword fallback)."""
        item = self.db.query(RawItem).filter(RawItem.item_id == raw_item_id).first()
        if not item:
            return []

        # Check for Gemini Key
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_key:
            return self._analyze_with_gemini(item, gemini_key)
        else:
            return self._analyze_with_keywords(item)

    def _analyze_with_gemini(self, item, api_key):
        """Use Google Gemini 1.5 Flash to analyze text."""
        import google.generativeai as genai
        
        print(f"🧠 AI-ANALYSIS: Processing Item {item.item_id} with Gemini...")
        genai.configure(api_key=api_key)
        # Using 2.5 Flash (Standard 2026 Model)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Analyze the following news item for an "AI Civilization Observer" system.
        
        SOURCE URL: {item.url}
        CONTENT:
        {item.content[:2000]}... (truncated)

        Task:
        1. Identify the single most critical claim or event.
        2. Classify its 'Civilization Impact Level' (L1-L5):
           - L5: Official Fact (Gov reports, Financial statements, Court rulings)
           - L4: Strong Evidence (Direct quotes, Data tables, Verifiable photos)
           - L3: Secondary Report (News summaries, Analysis)
           - L2: Social Chatter (Tweets, Forum posts)
           - L1: Speculation (Rumors, Predictions, 'Might', 'Could')
        3. Assess its Reliability (0.0 - 1.0).

        Return JSON only:
        {{
            "extract": "One sentence summary of the core event",
            "level": <int 1-5>,
            "reliability_score": <float 0.0-1.0>,
            "kind": "fact|inference|hazard|data"
        }}
        """

        try:
            response = model.generate_content(prompt)
            # Simple JSON cleanup (Gemini sometimes wraps in ```json ... ```)
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            # Construct Evidence
            evidence = Evidence(
                raw_item_id=item.item_id,
                cluster_id=None,
                level=data.get('level', 3),
                extract=data.get('extract', "AI Extraction Failed"),
                pointer={
                    "url": item.canonical_url or item.url,
                    "match_text": "Generative Analysis",
                    "source_hash": item.content_hash,
                    "model": "gemini-1.5-flash"
                },
                reliability_score=data.get('reliability_score', 0.5),
                evidence_kind=data.get('kind', 'inference')
            )
            
            self.db.add(evidence)
            self.db.commit()
            return [evidence]

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return self._analyze_with_keywords(item)

    def _analyze_with_keywords(self, item):
        """Legacy keyword-based extraction."""
        print("⚠️  Fallback: Using Keyword Analysis")
        extracted_evidence = []
        sentences = re.split(r'(?<=[.!?])\s+', item.content)
        
        is_official_source = item.source.source_type == 'official'
        
        for idx, sent in enumerate(sentences):
            if len(sent) < 20: continue 

            level = 3
            kind = 'fact'
            lower_sent = sent.lower()

            # L1: Inference
            if any(w in lower_sent for w in ['predicts', 'might', 'speculates', 'rumor']):
                level = 1
                kind = 'inference'
            # L2: Social
            elif 'twitter' in item.url or 'weibo' in item.url:
                level = 2
            # L5: Official
            elif is_official_source or 'official statement' in lower_sent or 'report' in lower_sent:
                level = 5
            # L4: Strong Secondary
            elif 'according to' in lower_sent:
                level = 4
                kind = 'quote'

            pointer = {
                "url": item.canonical_url or item.url,
                "match_text": sent[:50] + "...",
                "source_hash": item.content_hash,
                "captured_at": item.fetched_at.isoformat() if item.fetched_at else None
            }

            evidence = Evidence(
                raw_item_id=item.item_id,
                cluster_id=None,
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
