-- ==========================================
-- AI Civilization News: Supabase Init Script
-- Combined Schema + v1.1.1 Patch
-- ==========================================

BEGIN;

-- 1. SOURCES
CREATE TABLE IF NOT EXISTS sources (
  source_id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('rss','api','web','official')),
  url TEXT,
  reliability_baseline FLOAT DEFAULT 0.5,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. RAW ITEMS
CREATE TABLE IF NOT EXISTS raw_items (
  item_id SERIAL PRIMARY KEY,
  source_id INT REFERENCES sources(source_id),
  content_hash VARCHAR(64) UNIQUE NOT NULL,
  title TEXT,
  content TEXT,
  url TEXT,
  canonical_url TEXT,
  content_type VARCHAR(50) DEFAULT 'text/html',
  published_at TIMESTAMPTZ,
  fetched_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_raw_items_source_time ON raw_items(source_id, fetched_at DESC);

-- 3. EVENT CLUSTERS
CREATE TABLE IF NOT EXISTS event_clusters (
  cluster_id SERIAL PRIMARY KEY,
  domain VARCHAR(50) NOT NULL DEFAULT 'Human' CHECK (domain IN ('Universe','Earth','Human','Power','Tech','Culture')),
  cluster_state VARCHAR(50) NOT NULL DEFAULT 'Emerging' CHECK (cluster_state IN ('Emerging','Active','Stabilizing','Disputed','Retracted')),
  title VARCHAR(500),
  first_observed_at TIMESTAMPTZ DEFAULT NOW(),
  last_updated_at TIMESTAMPTZ DEFAULT NOW(),
  corrected_flag BOOLEAN DEFAULT FALSE,
  retraction_flag BOOLEAN DEFAULT FALSE,
  supersedes_cluster_id INT REFERENCES event_clusters(cluster_id)
);
CREATE INDEX IF NOT EXISTS idx_clusters_domain_state ON event_clusters(domain, cluster_state);
CREATE INDEX IF NOT EXISTS idx_clusters_updated ON event_clusters(last_updated_at DESC);

-- 4. EVIDENCE
CREATE TABLE IF NOT EXISTS evidence (
  evidence_id SERIAL PRIMARY KEY,
  raw_item_id INT REFERENCES raw_items(item_id),
  cluster_id INT REFERENCES event_clusters(cluster_id),
  level INT NOT NULL CHECK (level BETWEEN 1 AND 5),
  extract TEXT NOT NULL,
  pointer JSONB NOT NULL,
  reliability_score FLOAT,
  extracted_at TIMESTAMPTZ DEFAULT NOW(),
  evidence_kind VARCHAR(30) DEFAULT 'fact' CHECK (evidence_kind IN ('fact','quote','data','inference'))
);
ALTER TABLE evidence DROP CONSTRAINT IF EXISTS chk_pointer_has_url;
ALTER TABLE evidence ADD CONSTRAINT chk_pointer_has_url CHECK (pointer ? 'url');
CREATE INDEX IF NOT EXISTS idx_evidence_cluster_level ON evidence(cluster_id, level DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_raw_item ON evidence(raw_item_id);

-- 5. OBSERVATIONS
CREATE TABLE IF NOT EXISTS observations (
  observation_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  observation_type VARCHAR(50) NOT NULL CHECK (observation_type IN ('hypothesis','prediction','constraint')),
  state VARCHAR(50) DEFAULT 'Active' CHECK (state IN ('Active','Weakened','Falsified')),
  content TEXT,
  payload JSONB,
  evidence_ids INT[],
  gap_ids INT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. GAPS
CREATE TABLE IF NOT EXISTS gaps (
  gap_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  gap_level VARCHAR(20) NOT NULL CHECK (gap_level IN ('low','mid','high','audit')),
  description TEXT NOT NULL,
  needed_evidence_types TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. SCORES
CREATE TABLE IF NOT EXISTS cluster_scores (
  score_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  consistency FLOAT,
  mechanism_uncertainty FLOAT,
  risk FLOAT,
  contradiction_ratio FLOAT,
  computed_at TIMESTAMPTZ DEFAULT NOW(),
  method_version VARCHAR(50) DEFAULT 'governance_1.0'
);

-- 8. ACTIVITY LOG
CREATE TABLE IF NOT EXISTS cluster_activity_log (
  log_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  log_type VARCHAR(50) NOT NULL CHECK (log_type IN ('internal_tick','evidence_added','state_change','published','correction','retraction')),
  log_data JSONB NOT NULL,
  logged_at TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE cluster_activity_log DROP CONSTRAINT IF EXISTS chk_log_data_valid;
ALTER TABLE cluster_activity_log ADD CONSTRAINT chk_log_data_valid CHECK (jsonb_typeof(log_data) = 'object');

-- 9. PUBLISHED VERSIONS
CREATE TABLE IF NOT EXISTS published_versions (
  version_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  version_seq INT NOT NULL,
  version_label VARCHAR(20),
  published_at TIMESTAMPTZ DEFAULT NOW(),
  reason VARCHAR(255) NOT NULL CHECK (reason IN ('auto_60m','rapid_15m','active_30m','correction','retraction')),
  changed_sections TEXT[],
  added_evidence_ids INT[],
  score_delta JSONB,
  snapshot_payload JSONB NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_published_cluster_seq ON published_versions(cluster_id, version_seq);
ALTER TABLE published_versions DROP CONSTRAINT IF EXISTS chk_snapshot_payload_valid;
ALTER TABLE published_versions ADD CONSTRAINT chk_snapshot_payload_valid CHECK (snapshot_payload ? 'title' AND snapshot_payload ? 'domain');

-- ==========================================
-- TRIGGERS & FUNCTIONS (Patch v1.1.1)
-- ==========================================

-- Trigger: Update EventCluster timestamp on Evidence insert
CREATE OR REPLACE FUNCTION update_cluster_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE event_clusters
  SET last_updated_at = NOW()
  WHERE cluster_id = NEW.cluster_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_evidence_update_cluster ON evidence;
CREATE TRIGGER trg_evidence_update_cluster
AFTER INSERT OR UPDATE ON evidence
FOR EACH ROW
EXECUTE FUNCTION update_cluster_timestamp();

-- Table: Version Counters for concurrency safety
CREATE TABLE IF NOT EXISTS cluster_version_counters (
    cluster_id INT PRIMARY KEY REFERENCES event_clusters(cluster_id),
    last_seq INT DEFAULT 0
);

-- Function: Get Next Version Seq
CREATE OR REPLACE FUNCTION get_next_version_seq(p_cluster_id INT)
RETURNS INT AS $$
DECLARE
    next_val INT;
BEGIN
    INSERT INTO cluster_version_counters (cluster_id, last_seq)
    VALUES (p_cluster_id, 1)
    ON CONFLICT (cluster_id)
    DO UPDATE SET last_seq = cluster_version_counters.last_seq + 1
    RETURNING last_seq INTO next_val;
    
    RETURN next_val;
END;
$$ LANGUAGE plpgsql;

COMMIT;
