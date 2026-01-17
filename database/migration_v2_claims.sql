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
