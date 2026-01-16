from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.supa_client import get_supabase

router = APIRouter()

# DTOs
class ClusterListDTO(BaseModel):
    cluster_id: int
    title: str
    domain: str
    cluster_state: str
    last_updated_at: datetime

@router.get("/clusters", response_model=List[ClusterListDTO])
def get_clusters(domain: Optional[str] = None):
    supa = get_supabase()
    query = supa.table("event_clusters").select("cluster_id, title, domain, cluster_state, last_updated_at")
    
    if domain:
        query = query.eq("domain", domain)
        
    # Order by time DESC
    res = query.order("last_updated_at", desc=True).execute()
    return res.data

@router.get("/cluster/{cluster_id}")
def get_cluster_details(cluster_id: int):
    supa = get_supabase()
    
    # 1. Cluster Info
    c_res = supa.table("event_clusters").select("*").eq("cluster_id", cluster_id).execute()
    if not c_res.data:
        raise HTTPException(status_code=404, detail="Cluster not found")
        
    # 2. Evidence
    e_res = supa.table("evidence").select("*").eq("cluster_id", cluster_id).order("level", desc=True).execute()
    
    # 3. Latest Score
    s_res = supa.table("cluster_scores").select("*").eq("cluster_id", cluster_id).order("computed_at", desc=True).limit(1).execute()
    latest_score = s_res.data[0] if s_res.data else None
    
    return {
        "event_cluster": c_res.data[0],
        "evidence": e_res.data,
        "latest_score": latest_score
    }

@router.get("/state")
def get_system_state():
    return {"status": "ONLINE", "mode": "SUPABASE_CLOUD"}
