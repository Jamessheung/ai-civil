from sqlalchemy.orm import Session
from ..models import EventCluster, Evidence, ClusterScore, ClusterActivityLog
from sqlalchemy import func

class ScorerService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_cluster_score(self, cluster_id: int):
        """Calculate and save scores for a cluster."""
        cluster = self.db.query(EventCluster).filter(EventCluster.cluster_id == cluster_id).first()
        if not cluster: return

        evidence_list = self.db.query(Evidence).filter(Evidence.cluster_id == cluster_id).all()
        if not evidence_list: return

        # Metrics
        total_ev = len(evidence_list)
        l5_count = sum(1 for e in evidence_list if e.level == 5)
        l1_count = sum(1 for e in evidence_list if e.level == 1)
        
        # Consistency: Ratio of high quality evidence
        consistency = (l5_count + sum(1 for e in evidence_list if e.level == 4)) / total_ev if total_ev > 0 else 0

        # Risk: Ratio of speculative evidence (L1)
        risk = l1_count / total_ev if total_ev > 0 else 0

        # Mechanism Uncertainty: Simplified as 1 - consistency for MVP
        mechanism_uncertainty = 1.0 - consistency

        # Contradiction: Placeholder (needs NLP)
        contradiction_ratio = 0.0

        # Save Score
        score = ClusterScore(
            cluster_id=cluster_id,
            consistency=consistency,
            mechanism_uncertainty=mechanism_uncertainty,
            risk=risk,
            contradiction_ratio=contradiction_ratio,
            method_version='governance_1.0'
        )
        self.db.add(score)
        
        # We assume Heartbeat service handles the Activity Log based on deltas
        # But we commit the score here
        self.db.commit()
