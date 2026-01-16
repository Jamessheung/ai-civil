import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.supa_client import get_supabase
import hashlib
from datetime import datetime, timezone

def color(text, code): return f"\033[{code}m{text}\033[0m"

def seed_supabase():
    supa = get_supabase()
    print(color("☁️  Connecting to Supabase...", "36"))

    try:
        # Check if we have sources (sanity check to see if tables exist)
        res = supa.table("sources").select("count", count="exact").execute()
    except Exception as e:
        print(color(f"❌ Connection Failed: The tables probably don't exist yet.\n   Error: {e}", "31"))
        print("\n👉 Please run the 'database/supabase_full_init.sql' script in Supabase SQL Editor first!")
        return

    print(color("🌱 Seeding Mock Data into Cloud DB...", "36"))

    # 1. Insert Sources
    try:
        supa.table("sources").upsert([
            {"name": "Federal Reserve", "source_type": "official", "url": "https://federalreserve.gov", "reliability_baseline": 1.0},
            {"name": "Twitter User @user123", "source_type": "web", "url": "https://x.com/user123", "reliability_baseline": 0.2}
        ], on_conflict="name").execute()
        
        # Get IDs
        src_gov = supa.table("sources").select("source_id").eq("name", "Federal Reserve").single().execute().data
        src_twitter = supa.table("sources").select("source_id").eq("name", "Twitter User @user123").single().execute().data

        # 2. Raw Items
        hash1 = hashlib.sha256(b"Fed Report").hexdigest()
        hash2 = hashlib.sha256(b"Tech Rumor").hexdigest()

        supa.table("raw_items").upsert([
            {
                "source_id": src_gov['source_id'], "content_hash": hash1,
                "title": "Federal Reserve Report: Inflation Stabilizing",
                "content": "The Federal Reserve...", "url": "https://federalreserve.gov/reports/2026-q1",
                "published_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "source_id": src_twitter['source_id'], "content_hash": hash2,
                "title": "Rumor: Tech Giant collapsing?",
                "content": "My cousin works at OpenAI...", "url": "https://x.com/user123/status/999",
                "published_at": datetime.now(timezone.utc).isoformat()
            }
        ], on_conflict="content_hash").execute()

        # Get Item IDs
        item_gov = supa.table("raw_items").select("item_id").eq("content_hash", hash1).single().execute().data
        item_rumor = supa.table("raw_items").select("item_id").eq("content_hash", hash2).single().execute().data

        # 3. Clusters
        # Upsert by ID is tricky without known IDs. We'll check existence by title.
        c_gov = supa.table("event_clusters").select("cluster_id").eq("title", "Federal Reserve Report: Inflation Stabilizing").execute()
        
        cluster_gov_id = None
        if not c_gov.data:
            res = supa.table("event_clusters").insert({
                "title": "Federal Reserve Report: Inflation Stabilizing", "domain": "Power", "cluster_state": "Active"
            }).execute()
            cluster_gov_id = res.data[0]['cluster_id']
        else:
            cluster_gov_id = c_gov.data[0]['cluster_id']

        c_rumor = supa.table("event_clusters").select("cluster_id").eq("title", "Rumor: Tech Giant collapsing?").execute()
        cluster_rumor_id = None
        if not c_rumor.data:
            res = supa.table("event_clusters").insert({
                "title": "Rumor: Tech Giant collapsing?", "domain": "Tech", "cluster_state": "Disputed"
            }).execute()
            cluster_rumor_id = res.data[0]['cluster_id']
        else:
            cluster_rumor_id = c_rumor.data[0]['cluster_id']

        # 4. Evidence
        # Simply insert (ignoring dupes for this demo script logic simplicity)
        supa.table("evidence").insert([
            {
                "raw_item_id": item_gov['item_id'], "cluster_id": cluster_gov_id, "level": 5,
                "extract": "Data indicates inflation has stabilized at 2.1%.",
                "pointer": {"url": "https://gov...", "match_text": "Data indicates"},
                "reliability_score": 0.95
            },
            {
                "raw_item_id": item_rumor['item_id'], "cluster_id": cluster_rumor_id, "level": 2,
                "extract": "My cousin works at OpenAI...",
                "pointer": {"url": "https://x.com...", "match_text": "Cousin works"},
                "reliability_score": 0.2
            },
            {
                "raw_item_id": item_rumor['item_id'], "cluster_id": cluster_rumor_id, "level": 1,
                "extract": "It might be over guys.",
                "pointer": {"url": "https://x.com...", "match_text": "Might be over"},
                "reliability_score": 0.1
            }
        ]).execute()

        # 5. Scores
        supa.table("cluster_scores").insert([
            {"cluster_id": cluster_gov_id, "consistency": 1.0, "risk": 0.0},
            {"cluster_id": cluster_rumor_id, "consistency": 0.0, "risk": 0.8}
        ]).execute()

        print(color("✅ Seed Complete! Data is now in Supabase.", "1;32"))

    except Exception as e:
        print(color(f"⚠️  Seed partial/failed (Data might already exist): {e}", "33"))

if __name__ == "__main__":
    seed_supabase()
