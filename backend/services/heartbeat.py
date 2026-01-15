from sqlalchemy.orm import Session
from ..database import SessionLocal
from .ingestor import IngestorService
from .evidence_extractor import EvidenceExtractor
from .clusterer import ClustererService
from .scorer import ScorerService
from ..models import EventCluster, ClusterActivityLog, Evidence
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class HeartbeatService:
    def run_tick(self):
        """Execute one 10m tick (Ingest -> Extract -> Cluster -> Score)."""
        db = SessionLocal()
        try:
            logger.info("Starting Internal Tick...")
            
            # 1. Ingest
            ingestor = IngestorService(db)
            new_items = ingestor.ingest_all()
            
            # 2. Extract
            # For simplicity in MVP, we process ALL raw items that don't have evidence yet
            extractor = EvidenceExtractor(db)
            # Find raw items without evidence (naive check, or check raw_item.evidence relation)
            # Here we just iterate recent items or implement a queue. 
            # For MVP, let's process last 50 items to ensure we catch new ones
            # In production, use a queue.
            from ..models import RawItem
            recent_items = db.query(RawItem).order_by(RawItem.fetched_at.desc()).limit(50).all()
            
            new_evidence_count = 0
            for item in recent_items:
                if not item.evidence: # If no evidence linked
                    evs = extractor.process_item(item.item_id)
                    new_evidence_count += len(evs)
            
            # 3. Cluster
            clusterer = ClustererService(db)
            clusterer.cluster_evidence()
            
            # 4. Score
            scorer = ScorerService(db)
            active_clusters = db.query(EventCluster).filter(EventCluster.cluster_state.in_(['Emerging', 'Active'])).all()
            for cluster in active_clusters:
                scorer.calculate_cluster_score(cluster.cluster_id)
                self.log_tick(db, cluster.cluster_id)

            logger.info(f"Tick Complete. New Items: {new_items}, New Evidence: {new_evidence_count}")
        
        except Exception as e:
            logger.error(f"Tick Failed: {e}")
            db.rollback()
        finally:
            db.close()

    def log_tick(self, db: Session, cluster_id: int):
        """Generate structured log for a cluster."""
        # Calculate stats for this tick (simplified, assume accumulated checks or diffs)
        # For strict correctness, we'd need to know what changed *this tick*.
        # Here we log the *current state* snapshot as 'internal_tick' which is acceptable for MVP log stream
        
        evidence_list = db.query(Evidence).filter(Evidence.cluster_id == cluster_id).all()
        l5 = sum(1 for e in evidence_list if e.level == 5)
        l4 = sum(1 for e in evidence_list if e.level == 4)
        l3 = sum(1 for e in evidence_list if e.level == 3)
        l2 = sum(1 for e in evidence_list if e.level == 2)
        l1 = sum(1 for e in evidence_list if e.level == 1)

        log_data = {
            "method_version": "governance_1.0",
            "added_evidence_by_level": {
                "L5": l5, "L4": l4, "L3": l3, "L2": l2, "L1": l1
            },
            # "score_deltas": ... (omit for brevity in MVP)
        }

        log = ClusterActivityLog(
            cluster_id=cluster_id,
            log_type='internal_tick',
            log_data=log_data
        )
        db.add(log)
        db.commit()
