from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import EventCluster, Evidence, Observation, Gap, ClusterScore, PublishedVersion, ClusterActivityLog

router = APIRouter()

@router.get("/clusters")
def get_clusters(
    domain: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(EventCluster)
    if domain:
        query = query.filter(EventCluster.domain == domain)
    if state:
        query = query.filter(EventCluster.cluster_state == state)
    
    clusters = query.order_by(EventCluster.last_updated_at.desc()).limit(limit).all()
    return clusters

@router.get("/cluster/{cluster_id}")
def get_cluster_details(
    cluster_id: int,
    v: Optional[str] = None, # Version Sequence (integers as str)
    lens: Optional[str] = 'observer',
    db: Session = Depends(get_db)
):
    # Support ?v=SEQ logic
    if v and v.isdigit():
        # Replay Mode
        version = db.query(PublishedVersion).filter(
            PublishedVersion.cluster_id == cluster_id,
            PublishedVersion.version_seq == int(v)
        ).first()
        
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
        
        snapshot = version.snapshot_payload
        # Reconstruct from snapshot
        # Note: In strict mode we return the snapshot data directly
        # The frontend expects { event_cluster: ..., evidence: ... }
        
        return {
            "mode": "replay",
            "version": version,
            "evidence": snapshot.get('evidence_snapshot', []),
            "scores": snapshot.get('scores', {}),
            "lens_payload": snapshot.get('lens_payload', {}),
            "gaps": snapshot.get('gaps_snapshot', [])
        }

    # Live Mode
    cluster = db.query(EventCluster).filter(EventCluster.cluster_id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    evidence = db.query(Evidence).filter(Evidence.cluster_id == cluster_id).order_by(Evidence.level.desc()).all()
    observations = db.query(Observation).filter(Observation.cluster_id == cluster_id).all()
    gaps = db.query(Gap).filter(Gap.cluster_id == cluster_id).all()
    
    # Get latest score
    latest_score = db.query(ClusterScore).filter(ClusterScore.cluster_id == cluster_id).order_by(ClusterScore.computed_at.desc()).first()
    
    # Get versions
    versions = db.query(PublishedVersion).filter(PublishedVersion.cluster_id == cluster_id).order_by(PublishedVersion.version_seq.desc()).all()

    return {
        "mode": "live",
        "event_cluster": cluster,
        "evidence": evidence,
        "observations": observations,
        "gaps": gaps,
        "latest_score": latest_score,
        "versions": versions
    }

@router.get("/state")
def get_system_state(db: Session = Depends(get_db)):
    """Global system stats (mockup for MVP)."""
    total_clusters = db.query(EventCluster).count()
    total_evidence = db.query(Evidence).count()
    return {
        "heartbeat": "active",
        "cluster_count": total_clusters,
        "evidence_count": total_evidence
    }
