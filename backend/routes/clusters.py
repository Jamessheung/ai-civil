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
    # Civilization Spec v1.0 Fields
    scores: dict  # {consistency, risk, ...}
    evidence_counts: dict # {L5: 1, L4: 2...}
    deltas: dict # {evidence_weighted: 1.2, uncertainty: -0.05, claims: 1}
    times: dict # {tick: datetime, published: datetime, seq: int}
    lens_type: str # OBS or ANTH
    anthropic_scores: dict # {aix, aud}

@router.get("/clusters", response_model=List[ClusterListDTO])
def get_clusters(domain: Optional[str] = None):
    supa = get_supabase()
    
    # 1. Fetch Clusters
    query = supa.table("event_clusters").select("cluster_id, title, domain, cluster_state, last_updated_at")
    if domain:
        query = query.eq("domain", domain)
    clusters = query.order("last_updated_at", desc=True).execute().data
    
    if not clusters:
        return []
        
    cluster_ids = [c['cluster_id'] for c in clusters]
    
    # 2. Fetch Aggregates (Batch)
    # Evidence Counts
    evidence_data = supa.table("evidence").select("cluster_id, level").in_("cluster_id", cluster_ids).execute().data
    
    # Scores (Latest) - Ideally we use a view, but here we construct map
    scores_data = supa.table("cluster_scores").select("cluster_id, consistency, risk, mechanism_uncertainty, contradiction_ratio, computed_at").in_("cluster_id", cluster_ids).order("computed_at", desc=True).execute().data
    
    # Published Versions (Latest)
    versions_data = supa.table("published_versions").select("cluster_id, version_seq, published_at").in_("cluster_id", cluster_ids).order("version_seq", desc=True).execute().data
    
    # 3. Process Aggregates
    ev_map = {}
    for e in evidence_data:
        cid = e['cluster_id']
        lvl = f"L{e['level']}"
        if cid not in ev_map: ev_map[cid] = {'L5':0,'L4':0,'L3':0,'L2':0,'L1':0}
        ev_map[cid][lvl] += 1
        
    score_map = {}
    for s in scores_data:
        cid = s['cluster_id']
        if cid not in score_map: score_map[cid] = s # Take first (latest)
        
    ver_map = {}
    for v in versions_data:
        cid = v['cluster_id']
        if cid not in ver_map: ver_map[cid] = v
        
    # 4. Build DTOs
    result = []
    for c in clusters:
        cid = c['cluster_id']
        
        # Evidence
        counts = ev_map.get(cid, {'L5':0,'L4':0,'L3':0,'L2':0,'L1':0})
        
        # Scores
        s = score_map.get(cid, {'consistency':0.5, 'risk':0.5, 'mechanism_uncertainty':0.5, 'contradiction_ratio':0.1})
        
        # Times
        v = ver_map.get(cid, {})
        times = {
            "tick": c['last_updated_at'],
            "published": v.get('published_at'), # Can be None
            "seq": v.get('version_seq', 0)
        }
        
        # Deltas (Mock for v1.0, to be connected to real log later)
        # Logic: If Active, show some activity.
        import random
        deltas = {
            "evidence_weighted": round(random.uniform(0, 3.0), 1) if c['cluster_state'] in ['Active', 'Emerging'] else 0,
            "uncertainty": round(random.uniform(-0.1, 0.05), 2),
            "claims": random.randint(0, 2)
        }
        
        # Lens Logic
        # If AIx (mocked as reliability/consistency proxy) is high but AUD (uncertainty) is low -> ANTH?
        # Spec: if aix >= 0.5 && aud <= 0.35 -> ANTH
        # Let's map: score.consistency ~ AIx, score.mechanism_uncertainty ~ AUD
        aix = s.get('consistency', 0.5)
        aud = s.get('mechanism_uncertainty', 0.5)
        lens = "ANTH" if (aix >= 0.5 and aud <= 0.35) else "OBS"
        
        result.append({
            "cluster_id": cid,
            "title": c['title'],
            "domain": c['domain'],
            "cluster_state": c['cluster_state'],
            "scores": s,
            "evidence_counts": counts,
            "deltas": deltas,
            "times": times,
            "lens_type": lens,
            "anthropic_scores": {"aix": round(aix, 2), "aud": round(aud, 2)}
        })
        
    return result

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
    
    # 4. Claims (v2.0 Civilization Layer)
    claims_res = supa.table("claims").select("*").eq("cluster_id", cluster_id).execute()
    claims = claims_res.data
    
    return {
        "event_cluster": c_res.data[0],
        "evidence": e_res.data,
        "latest_score": latest_score,
        "claims": claims
    }

@router.get("/state")
def get_system_state():
    return {"status": "ONLINE", "mode": "SUPABASE_CLOUD"}
