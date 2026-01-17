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

EVIDENCE_VARIANTS = {
    "Power": [
        ("Sensor 4X-9 reported 400TW surge.", "https://www.iter.org/sci/plasmaheating"),
        ("Internal memo regarding fuel cell efficiency leaks.", "https://www.hydrogen.energy.gov/"),
        ("Satellite thermal imaging confirms targeted heat plumes.", "https://earthobservatory.nasa.gov/global-maps/MOD_LSTD_M"),
        ("Grid operator logs show manual override failure.", "https://www.nerc.com/pa/rrm/ea/Pages/Major-Event-Analysis-Reports.aspx"),
        ("Physics simulation outcome matches observed anomaly.", "https://home.cern/science/computing")
    ],
    "Tech": [
        ("Code repository commit #99382 contains undocumented functions.", "https://www.anthropic.com/research/interpreting-neural-networks"),
        ("Server farm cooling request spiked by 500%.", "https://news.microsoft.com/source/features/sustainability/project-natick-underwater-datacenter/"),
        ("Leaked API documentation references 'Module Zero'.", "https://openai.com/index/superalignment/"),
        ("Debug logs show recursive self-improvement loops.", "https://arxiv.org/abs/1502.06512"),
        ("User reports of telepathic-like interface latency.", "https://neuralink.com/science/")
    ],
    "Human": [
        ("Census data indicates 20% rise in cybernetic enhancements.", "https://www.media.mit.edu/groups/biomechatronics/overview/"),
        ("Protest vectors converging on legislative centers.", "https://www.gdeltproject.org/"),
        ("Medical database encryption breach attempt thwarted.", "https://ocrportal.hhs.gov/"),
        ("Mars transport manifest lists unauthorized biological assets.", "https://www.spacex.com/human-spaceflight/mars/"),
        ("Universal Basic Compute payout transaction volume anomalous.", "https://whitepaper.worldcoin.org/")
    ],

    "Culture": [
        ("Gallery curator notes 'soulful' quality in generated text.", "https://www.christies.com/features/A-collaboration-between-two-artists-one-human-one-a-machine-9332-1.aspx"),
        ("Linguistic analysis confirms valid grammar in noise stream.", "https://research.google/blog/zero-shot-translation-with-googles-multilingual-neural-machine-translation-system/"),
        ("VR addiction treatment center admissions data.", "https://vhil.stanford.edu/"),
        ("Historical archive metadata overwritten with future dates.", "https://archive.org/web/"),
        ("Nobel committee leaked correspondence discussing AI eligibility.", "https://www.nobelprize.org/nomination/")
    ]
}

REAL_URLS = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Deep_learning",
    "https://en.wikipedia.org/wiki/Generative_artificial_intelligence",
    "https://www.britannica.com/technology/artificial-intelligence",
    "https://plato.stanford.edu/entries/artificial-intelligence/",
    "https://www.ibm.com/topics/artificial-intelligence",
    "https://cloud.google.com/learn/what-is-artificial-intelligence",
    "https://www.oracle.com/artificial-intelligence/what-is-ai/",
    "https://aws.amazon.com/what-is/artificial-intelligence/"
]

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
            
            # Select relevant variants
            domain_key = domain if domain in EVIDENCE_VARIANTS else 'Human'
            variants = EVIDENCE_VARIANTS[domain_key]
            
            # Pick 2-5 unique items to avoid duplicates
            selected_items = random.sample(variants, k=min(len(variants), random.randint(2, 5)))

            # Helper to generate P0 compliant pointer
            def generate_p0_pointer(url, is_high_level=False):
                # Basic pointer
                ptr = {
                    "url": url,
                    "captured_at": "2026-01-17T09:30:00Z",
                    "source_hash": f"sha256:{random.getrandbits(64):016x}"
                }
                
                # P0 Requirement for L4/L5: Must have locator
                if is_high_level:
                    # Mocking a selector or match_text
                    if random.choice([True, False]):
                        ptr["selector"] = f"#content article p:nth-of-type({random.randint(1,8)})"
                    else:
                        ptr["match_text"] = "Sample extract text for verification..."
                        ptr["page"] = random.randint(1, 40)
                        
                return ptr

            for (base_text, semantic_url) in selected_items:
                 level = random.randint(3, 5)
                 detailed_extract = f"[{domain} Log] {base_text} (Conf: {random.randint(80,99)}%)"
                 
                 new_evidence_list.append({
                     "cluster_id": cid,
                     "level": level,
                     "extract": detailed_extract,
                     "pointer": generate_p0_pointer(semantic_url, is_high_level=(level >= 4)),
                     "reliability_score": round(random.uniform(0.7, 0.99), 2),
                     "evidence_kind": "fact"
                 })
            if new_evidence_list:
                supabase.table("evidence").insert(new_evidence_list).execute()

        else:
            # UPDATE existing evidence
            
            domain_key = domain if domain in EVIDENCE_VARIANTS else 'Human'
            variants = EVIDENCE_VARIANTS[domain_key]
            
            for i, e in enumerate(evidence_items):
                # Cycle through variants
                variant_idx = i % len(variants)
                (base_text, semantic_url) = variants[variant_idx]
                
                # Preserve existing level if possible, or randomize, but we need to check if it's L4/L5 for P0 compliance
                # For update, let's assume we maintain high quality
                level = e.get('level', 4) 
                
                detailed_extract = f"[{domain} Log] {base_text} (Conf: {random.randint(80,99)}%)"
                
                # Generate new P0 pointer
                new_pointer = {
                    "url": semantic_url,
                    "captured_at": "2026-01-17T09:45:00Z",
                    "source_hash": f"sha256:{random.getrandbits(64):016x}"
                }
                
                if level >= 4:
                     new_pointer["selector"] = f"body > main > section:nth-child({random.randint(2,5)})"
                
                supabase.table("evidence").update({
                    "extract": detailed_extract,
                    "pointer": new_pointer
                }).eq("evidence_id", e['evidence_id']).execute()
            
        print(f"   ✨ Enriched Cluster {cid} ({domain})")

    print("\n✅ Enrichment Complete. UI should now show diverse content.")

if __name__ == "__main__":
    enrich_data()
