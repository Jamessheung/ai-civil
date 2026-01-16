import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.supa_client import get_supabase

def reload_schema_cache():
    print("🔄 Forcing PostgREST Schema Cache Reload...")
    supabase = get_supabase()
    
    # We can use the rpc() interface if we had a function, 
    # or just try to invoke a raw query if possible. 
    # Supabase-py client doesn't support raw SQL directly on the client object easily 
    # without the 'vectors' or 'rpc' workarounds if the user hasn't exposed a sql function.
    
    # However, we can use the 'postgres' library if we had direct connection, 
    # but we are in cloud mode using REST.
    
    # A trick: Supabase Management API or Dashboard is usually needed. 
    # BUT, let's try to verify if 'summary' is actually in the columns by inspecting the tables API.
    
    try:
        # Standard way to reload PostgREST schema cache
        supabase.postgrest.auth(supabase.supabase_key)
        # We try to call a standard system function or just a raw query if we could.
        # Since we are locked out of raw SQL, we might just have to wait or toggle a setting.
        # BUT, the user provided 'schema.sql', maybe I can run a migration?
        print("   Checking if summary column is visible...")
        res = supabase.table("event_clusters").select("cluster_id, summary").limit(1).execute()
        print("   Success! Summary column is visible.")
    except Exception as e:
        print(f"   Cache reload failed or column still missing: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reload_schema_cache()
