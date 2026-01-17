import os, time
from sqlalchemy import text
from db import make_engine

ENGINE = make_engine()

def tick():
    with ENGINE.begin() as conn:
        cluster_ids = conn.execute(text("select cluster_id from event_clusters limit 100")).scalars().all()
        for cid in cluster_ids:
            conn.execute(text("""
                insert into cluster_activity_log (cluster_id, log_type, log_data)
                values (:cid, 'internal_tick', :log_data::jsonb)
            """), {
                "cid": cid,
                "log_data": '{"added_evidence_by_level":{"L5":0,"L4":0,"L3":0,"L2":0,"L1":0},"score_deltas":{},"method_version":"governance_1.0"}'
            })

def main():
    interval = int(os.environ.get("HEARTBEAT_SECONDS", "600"))  # default 10 min
    while True:
        try:
            tick()
            print("tick ok")
        except Exception as e:
            print("tick error:", e)
        time.sleep(interval)

if __name__ == "__main__":
    main()
