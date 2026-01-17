import os
import sys
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

def inject_breaking_news():
    print("🚨 Injecting BREAKING NEWS into Civilization Matrix...")
    supabase = get_supabase()
    
    # 1. Create Breaking Cluster
    title = f"BREAKING: Unknown Signal Detected from Sector {random.randint(100,999)}"
    payload = {
        "title": title,
        "domain": "Universe",
        "cluster_state": "Active",
        "summary": "High-frequency subspace resonance detected. Origin point triangulation indicates artificial source outside known colonial borders.",
        "first_observed_at": datetime.now().isoformat(),
        "last_updated_at": datetime.now().isoformat()
    }
    
    res = supabase.table("event_clusters").insert(payload).execute()
    new_cluster = res.data[0]
    cid = new_cluster['cluster_id']
    print(f"   [+] Cluster Created: ID {cid} - {title}")
    
    # 2. Add Evidence
    evidence_payload = {
        "cluster_id": cid,
        "level": 5,
        "extract": "[Universe Log] Signal pattern repeats prime number sequence. Logic gates confirmed. (Conf: 99.9%)",
        "reliability_score": 0.99,
        "evidence_kind": "data",
        "pointer": {
            "url": "https://www.nasa.gov/deep-space-network/realtime",
            "source": "Deep Space Network",
            "timestamp": datetime.now().isoformat()
        }
    }
    supabase.table("evidence").insert(evidence_payload).execute()
    print("   [+] Evidence Linked.")
    
    print("\n✅ Injection Complete. Refresh frontend to see the Breaking News.")

if __name__ == "__main__":
    inject_breaking_news()
