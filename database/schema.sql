-- =========================
-- AI Civilization News DB
-- Schema v1.1.1 (Base)
-- =========================

-- sources
CREATE TABLE sources (
  source_id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('rss','api','web','official')),
  url TEXT,
  reliability_baseline FLOAT DEFAULT 0.5,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- raw items
CREATE TABLE raw_items (
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

CREATE INDEX idx_raw_items_source_time ON raw_items(source_id, fetched_at DESC);

-- event clusters
CREATE TABLE event_clusters (
  cluster_id SERIAL PRIMARY KEY,
  domain VARCHAR(50) NOT NULL DEFAULT 'Human'
    CHECK (domain IN ('Universe','Earth','Human','Power','Tech','Culture')),
  cluster_state VARCHAR(50) NOT NULL DEFAULT 'Emerging'
    CHECK (cluster_state IN ('Emerging','Active','Stabilizing','Disputed','Retracted')),
  title VARCHAR(500),
  summary TEXT,
  first_observed_at TIMESTAMPTZ DEFAULT NOW(),
  last_updated_at TIMESTAMPTZ DEFAULT NOW(),
  corrected_flag BOOLEAN DEFAULT FALSE,
  retraction_flag BOOLEAN DEFAULT FALSE,
  supersedes_cluster_id INT REFERENCES event_clusters(cluster_id)
);

CREATE INDEX idx_clusters_domain_state ON event_clusters(domain, cluster_state);
CREATE INDEX idx_clusters_updated ON event_clusters(last_updated_at DESC);

-- evidence (L5 highest, L1 lowest)
CREATE TABLE evidence (
  evidence_id SERIAL PRIMARY KEY,
  raw_item_id INT REFERENCES raw_items(item_id),
  cluster_id INT REFERENCES event_clusters(cluster_id),
  level INT NOT NULL CHECK (level BETWEEN 1 AND 5),
  -- L5: primary/auditable record; L1: inference/speculation
  extract TEXT NOT NULL,
  pointer JSONB NOT NULL,
  reliability_score FLOAT,
  extracted_at TIMESTAMPTZ DEFAULT NOW(),
  -- optional: classify evidence assertion type
  evidence_kind VARCHAR(30) DEFAULT 'fact' CHECK (evidence_kind IN ('fact','quote','data','inference'))
);

-- pointer minimal schema enforcement (soft via CHECK on required keys)
ALTER TABLE evidence
  ADD CONSTRAINT chk_pointer_has_url
  CHECK (pointer ? 'url');

CREATE INDEX idx_evidence_cluster_level ON evidence(cluster_id, level DESC);
CREATE INDEX idx_evidence_raw_item ON evidence(raw_item_id);
CREATE INDEX idx_evidence_extracted ON evidence(extracted_at DESC);

-- observations (structured capable)
CREATE TABLE observations (
  observation_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  observation_type VARCHAR(50) NOT NULL
    CHECK (observation_type IN ('hypothesis','prediction','constraint')),
  state VARCHAR(50) DEFAULT 'Active'
    CHECK (state IN ('Active','Weakened','Falsified')),
  content TEXT,
  payload JSONB,
  evidence_ids INT[],
  gap_ids INT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_obs_cluster_time ON observations(cluster_id, created_at DESC);

-- gaps
CREATE TABLE gaps (
  gap_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  gap_level VARCHAR(20) NOT NULL CHECK (gap_level IN ('low','mid','high','audit')),
  description TEXT NOT NULL,
  needed_evidence_types TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_gaps_cluster ON gaps(cluster_id);

-- cluster scores
CREATE TABLE cluster_scores (
  score_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  consistency FLOAT,
  mechanism_uncertainty FLOAT,
  risk FLOAT,
  contradiction_ratio FLOAT,
  computed_at TIMESTAMPTZ DEFAULT NOW(),
  method_version VARCHAR(50) DEFAULT 'governance_1.0'
);

CREATE INDEX idx_scores_cluster_time ON cluster_scores(cluster_id, computed_at DESC);

-- activity log
CREATE TABLE cluster_activity_log (
  log_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  log_type VARCHAR(50) NOT NULL
    CHECK (log_type IN ('internal_tick','evidence_added','state_change','published','correction','retraction')),
  log_data JSONB NOT NULL,
  logged_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_log_cluster_time ON cluster_activity_log(cluster_id, logged_at DESC);

-- published versions (public)
CREATE TABLE published_versions (
  version_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  version_seq INT NOT NULL,
  version_label VARCHAR(20),
  published_at TIMESTAMPTZ DEFAULT NOW(),
  reason VARCHAR(255) NOT NULL
    CHECK (reason IN ('auto_60m','rapid_15m','active_30m','correction','retraction')),
  changed_sections TEXT[],
  added_evidence_ids INT[],
  score_delta JSONB,
  snapshot_payload JSONB NOT NULL
);

CREATE UNIQUE INDEX uq_published_cluster_seq ON published_versions(cluster_id, version_seq);
CREATE INDEX idx_published_cluster_time ON published_versions(cluster_id, published_at DESC);
-- AI Civilization v2.0: Claim Layer
-- Run this in Supabase SQL Editor

-- 1. Claims: 可被证实/证伪的最小语义单元
CREATE TABLE IF NOT EXISTS claims (
  claim_id SERIAL PRIMARY KEY,
  cluster_id INT REFERENCES event_clusters(cluster_id),
  content TEXT NOT NULL, -- e.g., "Model X uses synthetic data for training."
  claim_status VARCHAR(50) DEFAULT 'Unverified'
    CHECK (claim_status IN ('Supported', 'Disputed', 'Falsified', 'Unverified')),
  confidence_score FLOAT, -- Aggregated from evidence
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Claim Evidence Relation: 证据与断言的逻辑关系
CREATE TABLE IF NOT EXISTS claim_evidence (
  claim_id INT REFERENCES claims(claim_id),
  evidence_id INT REFERENCES evidence(evidence_id),
  relationship VARCHAR(20) NOT NULL 
    CHECK (relationship IN ('supports', 'refutes', 'irrelevant')),
  weight FLOAT DEFAULT 1.0,
  PRIMARY KEY (claim_id, evidence_id)
);

-- 3. Indexing for Audit Performance
CREATE INDEX IF NOT EXISTS idx_claims_cluster ON claims(cluster_id);
CREATE INDEX IF NOT EXISTS idx_claim_evidence_reverse ON claim_evidence(evidence_id);
