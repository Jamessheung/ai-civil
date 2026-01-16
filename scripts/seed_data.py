import sys
import os
import hashlib
from datetime import datetime, timezone

# Add backend to sys.path to import models
# Add project root to sys.path to import backend models
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from backend.database import SessionLocal, engine, Base
from backend.models import Source, RawItem, EventCluster, Evidence, ClusterScore, ClusterActivityLog

def color(text, code): return f"\033[{code}m{text}\033[0m"

def seed():
    db = SessionLocal()
    try:
        print(color("🌱 Seeding Database with Mock Events...", "36"))

        # 1. Sources
        src_gov = Source(name="Federal Reserve", source_type="official", url="https://federalreserve.gov", reliability_baseline=1.0)
        src_twitter = Source(name="Twitter User @user123", source_type="web", url="https://x.com/user123", reliability_baseline=0.2)
        
        # Check if exists
        if not db.query(Source).filter_by(name="Federal Reserve").first():
            db.add_all([src_gov, src_twitter])
            db.commit()
            print("   Created Sources")
        else:
            src_gov = db.query(Source).filter_by(name="Federal Reserve").first()
            src_twitter = db.query(Source).filter_by(name="Twitter User @user123").first()

        # 2. Raw Items
        hash1 = hashlib.sha256(b"Fed Report").hexdigest()
        item_gov = RawItem(
            source_id=src_gov.source_id,
            content_hash=hash1,
            title="Federal Reserve Report: Inflation Stabilizing",
            content="The Federal Reserve released its quarterly financial report today. Data indicates inflation has stabilized at 2.1%.",
            url="https://federalreserve.gov/reports/2026-q1",
            published_at=datetime.now(timezone.utc)
        )

        hash2 = hashlib.sha256(b"Tech Rumor").hexdigest()
        item_rumor = RawItem(
            source_id=src_twitter.source_id,
            content_hash=hash2,
            title="Rumor: Tech Giant collapsing?",
            content="My cousin works at OpenAI and says they are bankrupt. It might be over guys. #AI #Tech",
            url="https://x.com/user123/status/999",
            published_at=datetime.now(timezone.utc)
        )

        if not db.query(RawItem).filter_by(content_hash=hash1).first():
            db.add_all([item_gov, item_rumor])
            db.commit()
            print("   Created Raw Items")

        # 3. Clusters
        cluster_gov = EventCluster(title="Federal Reserve Report: Inflation Stabilizing", domain="Power", cluster_state="Active")
        cluster_rumor = EventCluster(title="Rumor: Tech Giant collapsing?", domain="Tech", cluster_state="Disputed") # Scorer would normally set this

        if not db.query(EventCluster).filter_by(title="Federal Reserve Report: Inflation Stabilizing").first():
            db.add_all([cluster_gov, cluster_rumor])
            db.commit()
            print("   Created Clusters")
        
        # Refresh to get IDs
        db.refresh(cluster_gov)
        db.refresh(cluster_rumor)
        db.refresh(item_gov)
        db.refresh(item_rumor)

        # 4. Evidence
        ev1 = Evidence(
            raw_item_id=item_gov.item_id, cluster_id=cluster_gov.cluster_id, level=5,
            extract="Data indicates inflation has stabilized at 2.1%.",
            pointer={"url": item_gov.url, "match_text": "Data indicates inflation"},
            reliability_score=0.9, evidence_kind="fact"
        )
        ev2 = Evidence(
            raw_item_id=item_rumor.item_id, cluster_id=cluster_rumor.cluster_id, level=2,
            extract="My cousin works at OpenAI and says they are bankrupt.",
            pointer={"url": item_rumor.url, "match_text": "My cousin works"},
            reliability_score=0.2, evidence_kind="quote"
        )
        ev3 = Evidence(
            raw_item_id=item_rumor.item_id, cluster_id=cluster_rumor.cluster_id, level=1,
            extract="It might be over guys.",
            pointer={"url": item_rumor.url, "match_text": "It might be over"},
            reliability_score=0.1, evidence_kind="inference"
        )

        # Naive check to avoid dupes if running multiple times
        if not db.query(Evidence).filter_by(extract="Data indicates inflation has stabilized at 2.1%.").first():
            db.add_all([ev1, ev2, ev3])
            db.commit()
            print("   Created Evidence")

        # 5. Scores
        score_gov = ClusterScore(cluster_id=cluster_gov.cluster_id, consistency=1.0, risk=0.0, mechanism_uncertainty=0.1)
        score_rumor = ClusterScore(cluster_id=cluster_rumor.cluster_id, consistency=0.0, risk=0.8, mechanism_uncertainty=0.9)
        db.add_all([score_gov, score_rumor])
        db.commit()
        print("   Created Scores")

        print(color("✅ Seed Complete! API will now return data.", "1;32"))

    except Exception as e:
        print(color(f"❌ Seed Failed: {e}", "1;31"))
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
