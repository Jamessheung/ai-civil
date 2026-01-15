from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Evidence, EventCluster, RawItem
from datetime import datetime
import math

class ClustererService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Naive Jaccard similarity for MVP."""
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def guess_domain(self, text: str) -> str:
        """Assign domain based on keywords."""
        text = text.lower()
        if 'planet' in text or 'nasa' in text or 'space' in text: return 'Universe'
        if 'climate' in text or 'earth' in text or 'environment' in text: return 'Earth'
        if 'policy' in text or 'election' in text or 'law' in text: return 'Power'
        if 'ai' in text or 'tech' in text or 'code' in text: return 'Tech'
        if 'art' in text or 'culture' in text or 'movie' in text: return 'Culture'
        return 'Human' # Default

    def cluster_evidence(self):
        """Group unclustered evidence into clusters."""
        # Get unclustered evidence
        unclustered = self.db.query(Evidence).filter(Evidence.cluster_id == None).all()
        
        for ev in unclustered:
            # 1. Try to find existing cluster
            # Look for active clusters updated recently
            active_clusters = self.db.query(EventCluster).filter(
                EventCluster.cluster_state.in_(['Emerging', 'Active'])
            ).all()

            best_cluster = None
            best_score = 0.3 # Threshold

            for cluster in active_clusters:
                sim = self.calculate_similarity(ev.extract, cluster.title)
                if sim > best_score:
                    best_score = sim
                    best_cluster = cluster
            
            if best_cluster:
                # Add to existing cluster
                ev.cluster_id = best_cluster.cluster_id
                # Touch cluster (Trigger will handle last_updated_at, but we might want explicit logic here too)
                # But we rely on patch trigger.
            else:
                # Create new cluster
                domain = self.guess_domain(ev.extract)
                new_cluster = EventCluster(
                    title=ev.extract[:100] + "...", # Simplified title from extract
                    domain=domain,
                    cluster_state='Emerging'
                )
                self.db.add(new_cluster)
                self.db.commit() # Commit to get ID
                self.db.refresh(new_cluster)
                
                ev.cluster_id = new_cluster.cluster_id
        
        self.db.commit()
