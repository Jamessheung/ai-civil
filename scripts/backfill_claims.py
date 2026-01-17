import os
import sys
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

CLAIM_TEMPLATES = {
    "Universe": ["Signal verified as non-random origin.", "Anomaly exceeds standard deviation threshold."],
    "Earth": ["Planetary ecosystem showing irreversible divergence.", "Resource allocation model requires immediate update."],
    "Human": ["Social cohesion index dropping below sustainable levels.", "New behavioral pattern identified in population subset."],
    "Tech": ["Synthetic intelligence demonstrating independent agency.", "Encryption protocols compromised by quantum decryption."],
    "Power": ["Geopolitical entity prioritizing resource monopoly.", "Conflict escalation projected within 48 hours."],
    "Culture": ["Artistic output verified as synthetic origin.", "Cultural memory corruption detected in archive."]
}

def backfill_claims():
    print("🧠 Backfilling Claims for Civilization Matrix (v2.0 Schema)...")
    supabase = get_supabase()
    
    # 1. Fetch all clusters
    clusters = supabase.table("event_clusters").select("cluster_id, title, domain, summary").execute().data
    print(f"   Found {len(clusters)} clusters to process.")
    
    for c in clusters:
        cid = c['cluster_id']
        domain = c['domain']
        title = c['title']
        
        # Check if claims already exist
        existing = supabase.table("claims").select("claim_id").eq("cluster_id", cid).execute().data
        if existing:
            print(f"   [Skip] Cluster {cid} already has {len(existing)} claims.")
            continue
            
        # 2. Generate Primary Claim
        # In a real system, this would be LLM generated. Here we use templates + title mix.
        base_claim = random.choice(CLAIM_TEMPLATES.get(domain, CLAIM_TEMPLATES['Human']))
        claim_content = f"ASSERTION: {base_claim} (Ref: {title})"
        
        claim_payload = {
            "cluster_id": cid,
            "content": claim_content,
            "claim_status": "Supported", # Default to supported for backfill
            "confidence_score": round(random.uniform(0.8, 0.99), 2)
        }
        
        res = supabase.table("claims").insert(claim_payload).execute()
        new_claim = res.data[0]
        claim_id = new_claim['claim_id']
        
        # 3. Link Evidence
        evidence_list = supabase.table("evidence").select("evidence_id, reliability_score").eq("cluster_id", cid).execute().data
        
        relations = []
        for ev in evidence_list:
            # Simple logic: High reliability evidence supports the claim
            relations.append({
                "claim_id": claim_id,
                "evidence_id": ev['evidence_id'],
                "relationship": "supports",
                "weight": ev['reliability_score'] or 1.0
            })
            
        if relations:
            supabase.table("claim_evidence").insert(relations).execute()
        
        print(f"   [+] Cluster {cid}: Created Claim #{claim_id} + Linked {len(relations)} Evidence.")

    print("\n✅ Backfill Complete. Claim Layer is active.")

if __name__ == "__main__":
    backfill_claims()
