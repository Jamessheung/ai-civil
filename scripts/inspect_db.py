import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

def inspect_db():
    print("🔍 Inspecting DB Content...")
    supabase = get_supabase()
    
    # Count clusters
    res = supabase.table("event_clusters").select("*", count="exact").execute()
    count = res.count
    print(f"Items in 'event_clusters': {count}")
    
    # List IDs
    if count > 0:
        ids = [str(item['cluster_id']) for item in res.data]
        print(f"IDs found: {', '.join(ids[:10])} ...")

if __name__ == "__main__":
    inspect_db()
