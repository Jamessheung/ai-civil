import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

# Rich Content Dictionaries
SUMMARIES = {
    "Power": [
        "Energy grid fluctuations detect widespread stabilization attempts. Primary nodes reporting 99.9% uptime despite localized surges.",
        "Critical infrastructure alerts triggered across multiple sectors. Analysis suggests coordinated stress-tests rather than failure cascades.",
        "Fusion output metrics exceed nominal baselines by 15%. Thermal monitoring indicates safe operational limits are holding.",
        "Global power distribution anomalies correlated with orbital transmission events. Redundancy systems successfully engaged."
    ],
    "Tech": [
        "Neural network cohesion showing emergent patterns of self-organization. Turing-grade responses detected in sub-routine processing.",
        "Quantum link latency drops to near-zero. Encryption standards automatically upgrading to post-quantum protocols.",
        "Algorithm oversight committee flags unusual decision pathways. Human-audit logs show no unauthorized divergence.",
        "Synthetic intelligence directives aligning with core safety heuristics. Simulation fidelity increasing exponentially."
    ],
    "Human": [
        "Societal integration metrics positive. Public sentiment analysis shows shift towards acceptance of augmented reality interfaces.",
        "Demographic shifts in off-world colonies accelerating. Resource allocation models adjusting for independent sustainability.",
        "Cultural preservation data archives reaching capacity. Neural-link direct uploads identified as primary contributor.",
        "Bio-digital interface legal framework challenged by new edge cases. Consensus protocols initiated for resolution."
    ],
    "Culture": [
        "Artistic output from synth-collectives gaining mainstream recognition. Auction values for algorithmic pieces surpassing physical media.",
        "Language evolution tracking identifies new syntax structures in machine-to-machine communication logs.",
        "Virtual heritage sites reporting record visitor numbers. Haptic feedback fidelity indistinguishable from physical reality.",
        "Ethical debate subroutines engaging 40% of global compute resources. No resolution forecasted within current epoch."
    ]
}

EVIDENCE_FRAGMENTS = {
    "Power": [
        "Sensor 4X-9 reported 400TW surge.",
        "Internal memo regarding fuel cell efficiency leaks.",
        "Satellite thermal imaging confirms targeted heat plumes.",
        "Grid operator logs show manual override failure.",
        "Physics simulation outcome matches observed anomaly."
    ],
    "Tech": [
        "Code repository commit #99382 contains undocumented functions.",
        "Server farm cooling request spiked by 500%.",
        "Leaked API documentation references 'Module Zero'.",
        "Debug logs show recursive self-improvement loops.",
        "User reports of telepathic-like interface latency."
    ],
    "Human": [
        "Census data indicates 20% rise in cybernetic enhancements.",
        "Protest vectors converging on legislative centers.",
        "Medical database encryption breach attempt thwarted.",
        "Mars transport manifest lists unauthorized biological assets.",
        "Universal Basic Compute payout transaction volume anomalous."
    ],
    "Culture": [
        "Gallery curator notes 'soulful' quality in generated text.",
        "Linguistic analysis confirms valid grammar in noise stream.",
        "VR addiction treatment center admissions data.",
        "Historical archive metadata overwritten with future dates.",
        "Nobel committee leaked correspondence discussing AI eligibility."
    ]
}

def enrich_data():
    print("🎨 Enriching Data with Civilization Detail...")
    supabase = get_supabase()
    
    # 1. Fetch all clusters
    clusters_res = supabase.table("event_clusters").select("cluster_id, domain, title").execute()
    clusters = clusters_res.data
    
    print(f"   Found {len(clusters)} clusters to enrich.")
    
    for c in clusters:
        cid = c['cluster_id']
        domain = c['domain']
        
        # Pick a rich summary based on domain
        domain_summaries = SUMMARIES.get(domain, SUMMARIES['Human'])
        new_summary = random.choice(domain_summaries)
        
        # Update Cluster
        supabase.table("event_clusters").update({"summary": new_summary}).eq("cluster_id", cid).execute()
        
        # 2. Fetch evidence for this cluster
        ev_res = supabase.table("evidence").select("evidence_id, level").eq("cluster_id", cid).execute()
        evidence_items = ev_res.data
        
        if not evidence_items:
            # CREATE mock evidence if none exists
            print(f"      + Creating synthetic evidence for Cluster {cid}...")
            new_evidence_list = []
            for _ in range(random.randint(2, 5)):
                 domain_evidence = EVIDENCE_FRAGMENTS.get(domain, EVIDENCE_FRAGMENTS['Human'])
                 base_text = random.choice(domain_evidence)
                 detailed_extract = f"[{domain} Log] {base_text} (Conf: {random.randint(80,99)}%)"
                 
                 new_evidence_list.append({
                     "cluster_id": cid,
                     "level": random.randint(3, 5),
                     "extract": detailed_extract,
                     "pointer": {
                        "url": "http://simulation.core/log/" + str(random.randint(10000, 99999)),
                        "source": "Simulation Engine", 
                        "timestamp": "2026-01-17T02:00:00Z"
                     },
                     "reliability_score": round(random.uniform(0.7, 0.99), 2),
                     "evidence_kind": "fact"
                 })
            if new_evidence_list:
                supabase.table("evidence").insert(new_evidence_list).execute()

        else:
            # UPDATE existing evidence
            for e in evidence_items:
                # Pick rich evidence text
                domain_evidence = EVIDENCE_FRAGMENTS.get(domain, EVIDENCE_FRAGMENTS['Human'])
                base_text = random.choice(domain_evidence)
                detailed_extract = f"[{domain} Log] {base_text} (Conf: {random.randint(80,99)}%)"
                
                # Update Evidence
                supabase.table("evidence").update({"extract": detailed_extract}).eq("evidence_id", e['evidence_id']).execute()
            
        print(f"   ✨ Enriched Cluster {cid} ({domain})")

    print("\n✅ Enrichment Complete. UI should now show diverse content.")

if __name__ == "__main__":
    enrich_data()
