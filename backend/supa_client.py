import os
from supabase import create_client, Client

# Prioritize Env Vars for Deployment, Fallback to Hardcoded for Local Dev
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://surzmukijrpoqtezuseb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cnptdWtpanJwb3F0ZXp1c2ViIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODU3Njg1MSwiZXhwIjoyMDg0MTUyODUxfQ.bLffh0THiBnyH5mU53Mw7iHnOh9ZRtVdJpsFl07bIME")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)
