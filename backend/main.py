import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db import make_engine, db_ping

app = FastAPI(title="AI Civilization Observer API", version="0.1.0")

allowed = os.environ.get("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in allowed.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = make_engine()

@app.get("/health")
def health():
    db_ping(engine)
    return {"status": "ok"}

@app.get("/api/state")
def state():
    # minimal; later expand to civilization strip
    with engine.connect() as conn:
        active = conn.execute(text("""
            select count(*) from event_clusters
            where cluster_state in ('Emerging','Active','Disputed','Stabilizing')
        """)).scalar_one()
    return {"active_clusters_count": int(active)}

@app.get("/api/clusters")
def clusters(state: str = "Active"):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            select
              c.cluster_id,
              c.title,
              c.domain,
              c.cluster_state,
              cs.consistency,
              cs.mechanism_uncertainty,
              cs.risk,
              cs.contradiction_ratio,
              cs.computed_at
            from event_clusters c
            left join lateral (
              select * from cluster_scores
              where cluster_id = c.cluster_id
              order by computed_at desc
              limit 1
            ) cs on true
            where (:state = 'All' or c.cluster_state = :state)
            order by c.last_updated_at desc
            limit 50
        """), {"state": state}).mappings().all()
    return {"clusters": [dict(r) for r in rows]}
