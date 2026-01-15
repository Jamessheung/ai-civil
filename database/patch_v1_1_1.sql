-- =========================
-- AI Civilization News DB
-- Patch v1.1.1 (Mandatory Execution)
-- =========================

-- 1. Trigger: event_clusters.last_updated_at
CREATE OR REPLACE FUNCTION set_last_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.last_updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_event_clusters_last_updated ON event_clusters;
CREATE TRIGGER trg_event_clusters_last_updated
BEFORE UPDATE ON event_clusters
FOR EACH ROW EXECUTE FUNCTION set_last_updated_at();

-- 2. Trigger: Touch Cluster on Evidence/Obs/Gap Insert
CREATE OR REPLACE FUNCTION touch_cluster_last_updated() RETURNS TRIGGER AS $$
BEGIN
  UPDATE event_clusters SET last_updated_at = NOW() WHERE cluster_id = NEW.cluster_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_evidence_touch_cluster ON evidence;
CREATE TRIGGER trg_evidence_touch_cluster
AFTER INSERT ON evidence
FOR EACH ROW EXECUTE FUNCTION touch_cluster_last_updated();

DROP TRIGGER IF EXISTS trg_obs_touch_cluster ON observations;
CREATE TRIGGER trg_obs_touch_cluster
AFTER INSERT ON observations
FOR EACH ROW EXECUTE FUNCTION touch_cluster_last_updated();

DROP TRIGGER IF EXISTS trg_gaps_touch_cluster ON gaps;
CREATE TRIGGER trg_gaps_touch_cluster
AFTER INSERT ON gaps
FOR EACH ROW EXECUTE FUNCTION touch_cluster_last_updated();

-- 3. Constraint: Log Data Structure (Minimal)
ALTER TABLE cluster_activity_log
  ADD CONSTRAINT chk_log_data_structure
  CHECK (log_data ? 'added_evidence_by_level' AND log_data ? 'method_version');

-- 4. Constraint: Snapshot Structure (Strict Minimal)
ALTER TABLE published_versions
  DROP CONSTRAINT IF EXISTS chk_snapshot_structure;

ALTER TABLE published_versions
  ADD CONSTRAINT chk_snapshot_structure
  CHECK (
    snapshot_payload ? 'evidence_ids' AND
    snapshot_payload ? 'evidence_snapshot' AND
    snapshot_payload ? 'scores' AND
    snapshot_payload ? 'lens_payload'
  );

-- 5. version_seq Auto-Increment (Concurrency-safe)
CREATE TABLE IF NOT EXISTS cluster_version_counters (
  cluster_id INT PRIMARY KEY REFERENCES event_clusters(cluster_id),
  last_seq INT NOT NULL DEFAULT 0
);

CREATE OR REPLACE FUNCTION assign_version_seq() RETURNS TRIGGER AS $$
DECLARE cur_seq INT;
BEGIN
  IF NEW.version_seq IS NULL THEN
    INSERT INTO cluster_version_counters (cluster_id, last_seq)
    VALUES (NEW.cluster_id, 0)
    ON CONFLICT (cluster_id) DO NOTHING;

    SELECT last_seq INTO cur_seq
    FROM cluster_version_counters
    WHERE cluster_id = NEW.cluster_id
    FOR UPDATE;

    cur_seq := cur_seq + 1;

    UPDATE cluster_version_counters
    SET last_seq = cur_seq
    WHERE cluster_id = NEW.cluster_id;

    NEW.version_seq := cur_seq;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_assign_version_seq ON published_versions;
CREATE TRIGGER trg_assign_version_seq
BEFORE INSERT ON published_versions
FOR EACH ROW EXECUTE FUNCTION assign_version_seq();
