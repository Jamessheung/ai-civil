import time
import json
import re

# --- MOCK LOGIC (Replicating Backend Services) ---

def color(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

class MockIngestor:
    def fetch(self):
        print(color("\n[1] INGESTOR: Scanning Global Sources...", "36"))
        time.sleep(0.5)
        return [
            {
                "id": 101,
                "title": "Federal Reserve Report: Inflation Stabilizing",
                "content": "The Federal Reserve released its quarterly financial report today. Data indicates inflation has stabilized at 2.1%. Analysts predict a rate cut is possible.",
                "source": "Official Gov Feed",
                "type": "official",
                "url": "https://gov.federalreserve.org/reports/2026-q1"
            },
            {
                "id": 102,
                "title": "Rumor: Tech Giant collapsing?",
                "content": "My cousin works at OpenAI and says they are bankrupt. It might be over guys. #AI #Tech",
                "source": "Twitter/X",
                "type": "social",
                "url": "https://x.com/user123/status/999"
            }
        ]

class MockExtractor:
    def process(self, item):
        print(f"    Processing: {item['title']}...")
        time.sleep(0.3)
        evidence = []
        sentences = item['content'].split('. ')
        
        for sent in sentences:
            if not sent: continue
            level = 3
            if item['type'] == 'official' or 'report' in sent.lower():
                level = 5  # L5: Official
            elif 'predict' in sent.lower() or 'might' in sent.lower():
                level = 1  # L1: Inference
            elif item['type'] == 'social':
                level = 2  # L2: Noise
            
            ptr = f"{item['url']}#:~:text={sent[:10]}"
            print(f"      -> Extracted: [{self.get_level_badge(level)}] {sent[:40]}... (Ptr: {ptr})")
            evidence.append({"level": level, "text": sent})
        return evidence

    def get_level_badge(self, level):
        if level == 5: return color("L5 OFFICIAL", "42;30") # Green bg
        if level == 4: return color("L4 STRONG", "44;30")   # Blue bg
        if level == 3: return color("L3 MEDIA", "43;30")    # Yellow bg
        if level == 2: return color("L2 NOISE", "41;30")    # Red bg
        if level == 1: return color("L1 INFER", "45;30")    # Purple bg
        return "UNK"

class MockClusterer:
    def cluster(self, items):
        print(color("\n[2] CLUSTERER: Analyzing Domains...", "36"))
        time.sleep(0.5)
        clusters = []
        for item in items:
            domain = "Human" # Default
            text = item['title'].lower() + item['content'].lower()
            if 'inflation' in text or 'money' in text: domain = "Power"
            if 'tech' in text or 'ai' in text: domain = "Tech"
            
            print(f"    Item '{item['title'][:20]}...' assigned to Domain: " + color(f"[{domain}]", "1;33"))
            clusters.append({"domain": domain, "title": item['title'], "evidence": item['evidence']})
        return clusters

class MockScorer:
    def score(self, cluster):
        print(color(f"\n[3] SCORER: Computing Metrics for Cluster '{cluster['title']}'...", "36"))
        time.sleep(0.3)
        
        ev_levels = [e['level'] for e in cluster['evidence']]
        l5 = ev_levels.count(5)
        l1 = ev_levels.count(1)
        total = len(ev_levels)
        
        consistency = (l5 / total) * 100
        risk = (l1 / total) * 100
        
        print(f"     Consistency: {consistency:.1f}% " + ("(HIGH)" if consistency > 80 else "(LOW)"))
        print(f"     Risk Score : {risk:.1f}% " + ("(WARNING)" if risk > 0 else "(SAFE)"))
        
        if consistency > 50 and risk < 20:
             print(color("    [GOVERNANCE RESULT]: STATUS = ACTIVE (PUBLISH)", "1;32"))
        else:
             print(color("    [GOVERNANCE RESULT]: STATUS = DISPUTED (HOLD)", "1;31"))

# --- RUNNER ---

def main():
    print(color("=== AI CIVILIZATION OBSERVER (v1.1.1) ===", "1;37"))
    print("Initializing Governance Protocols...\n")
    
    # 1. Ingest
    ingestor = MockIngestor()
    raw_items = ingestor.fetch()
    
    # 2. Extract
    extractor = MockExtractor()
    processed_items = []
    for item in raw_items:
        item['evidence'] = extractor.process(item)
        processed_items.append(item)
        
    # 3. Cluster
    clusterer = MockClusterer()
    clusters = clusterer.cluster(processed_items)
    
    # 4. Score
    scorer = MockScorer()
    for c in clusters:
        scorer.score(c)

    print(color("\n=== SIMULATION COMPLETE ===", "1;37"))
    print("System active. Waiting for next 10m tick.")

if __name__ == "__main__":
    main()
