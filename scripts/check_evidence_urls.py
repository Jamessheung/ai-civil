
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

def check_urls():
    supa = get_supabase()
    res = supa.table("evidence").select("evidence_id, pointer").limit(10).execute()
    for item in res.data:
        print(json.dumps(item['pointer'], indent=2))

if __name__ == "__main__":
    check_urls()
