import os
import sys
import random
from datetime import datetime, timedelta
import asyncio

# Fix path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.supa_client import get_supabase

# Initialize Client
supabase_client = get_supabase()
from backend.models import EventCluster, Evidence

# Mock Content Templates
TEMPLATES = {
    "Power": [
        "Fusion Reactor Stability Reached in {location}",
        "Global Energy Grid Protocol {protocol} Ratified",
        "Dyson Swarm Construction: Phase {phase} Begins",
        "Antimatter Containment Breach at {location}",
        "Helium-3 Supply Chain Disruption"
    ],
    "Tech": [
        "AI Model {model_name} Achieves Consciousness Level {level}",
        "Neural Link V{version} Approved for Human Trials",
        "Quantum Internet Node Online in {location}",
        "Autonomous Drones Declare Sovereignty in {region}",
        "Legacy TCP/IP Replaced by {protocol}"
    ],
    "Human": [
        "Universal Basic Compute (UBC) Act Passed",
        "First Digital-Biological Hybrid Citizen Registered",
        "Mars Colony {colony} Declares Independence",
        "Memory Recording Technology Banned in {region}",
        "Telepathy Interface Standardized"
    ],
    "Culture": [
        "AI Artist {artist} Wins Nobel Prize",
        "Archaeological Discovery: Pre-AI Data Center",
        "New Language '{lang}' Emerges Among Synthetics",
        "Virtual Reality Addiction Classified as Epidemic",
        "Preservation of Biological Heritage Act"
    ]
}

LOCATIONS = ["Neo-Tokyo", "Sector 7", "Mars Outpost Alpha", "Orbital Station One", "Silicon Valley", "Shenzhen Core", "London Underground"]
PROTOCOLS = ["Omega", "Zeta", "Flux", "Nexus", "Void"]
MODELS = ["Gemma-9", "GPT-X", "Claude-Omni", "DeepMind-Zero"]

def generate_mock_data():
    print("🌌 Initializing Big Bang: Seeding 30 Clusters...")
    
    clusters_to_insert = []
    evidence_to_insert = []
    
    # Generate 30 Events
    for i in range(30):
        domain = random.choice(list(TEMPLATES.keys()))
        template = random.choice(TEMPLATES[domain])
        
        # Fill template
        title = template.format(
            location=random.choice(LOCATIONS),
            protocol=random.choice(PROTOCOLS),
            phase=random.randint(1, 10),
            model_name=random.choice(MODELS),
            level=random.randint(5, 9),
            version=random.randint(10, 20),
            region="Sector " + str(random.randint(1, 100)),
            colony="Ares-" + str(random.randint(1, 5)),
            artist="Unit-" + str(random.randint(1000, 9999)),
            lang="Binary-K"
        )
        
        # Create Cluster Payload
        cluster_payload = {
            "title": title,
            "domain": domain,
            "cluster_state": random.choice(["Active", "Emerging", "Disputed"]),
            "last_updated_at": (datetime.now() - timedelta(minutes=random.randint(1, 600))).isoformat()
        }
        
        # In a real app we'd get the ID back, but for bulk insert via Supabase-py 
        # it's often easier to insert one by one or trust the DB to auto-increment.
        # Let's insert cluster first to get ID.
        try:
            res = supabase_client.table("event_clusters").insert(cluster_payload).execute()
            if not res.data:
                continue
                
            cluster_id = res.data[0]['cluster_id']
            print(f"   [+] Created Cluster {cluster_id}: {title}")
            
            # Generate 3-5 Random Evidence Pieces per Cluster
            for _ in range(random.randint(3, 5)):
                level = random.choice([1, 2, 3, 4, 5])
                evidence_payload = {
                    "cluster_id": cluster_id,
                    "raw_item_id": None, # Synthetic
                    "level": level,
                    "extract": f"Synthetic evidence regarding {title}. Level {level} signal detected.",
                    "evidence_kind": "fact" if level >= 4 else "inference",
                    "reliability_score": round(random.uniform(0.5, 0.99), 2),
                    "pointer": {
                        "url": "http://simulation.core/log/" + str(random.randint(1000, 9999)),
                        "match_text": "Simulation Log Entry",
                        "source": "Simulation Engine", 
                        "timestamp": datetime.now().isoformat()
                    }
                }
                supabase_client.table("evidence").insert(evidence_payload).execute()
                
        except Exception as e:
            print(f"   [!] Error seeding cluster: {e}")

    print("\n✅ Matrix Population Complete. Refresh Frontend.")

if __name__ == "__main__":
    generate_mock_data()
