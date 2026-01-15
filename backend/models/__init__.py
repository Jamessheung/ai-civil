from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, CheckConstraint, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Source(Base):
    __tablename__ = "sources"

    source_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)
    url = Column(Text)
    reliability_baseline = Column(Float, default=0.5)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    raw_items = relationship("RawItem", back_populates="source")

    __table_args__ = (
        CheckConstraint("source_type IN ('rss', 'api', 'web', 'official')", name='chk_source_type'),
    )

class RawItem(Base):
    __tablename__ = "raw_items"

    item_id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.source_id"))
    content_hash = Column(String(64), unique=True, nullable=False)
    title = Column(Text)
    content = Column(Text)
    url = Column(Text)
    canonical_url = Column(Text)
    content_type = Column(String(50), default='text/html')
    published_at = Column(TIMESTAMP(timezone=True))
    fetched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    source = relationship("Source", back_populates="raw_items")
    evidence = relationship("Evidence", back_populates="raw_item")

class EventCluster(Base):
    __tablename__ = "event_clusters"

    cluster_id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(50), nullable=False, default='Human')
    cluster_state = Column(String(50), nullable=False, default='Emerging')
    title = Column(String(500))
    first_observed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    corrected_flag = Column(Boolean, default=False)
    retraction_flag = Column(Boolean, default=False)
    supersedes_cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))

    evidence = relationship("Evidence", back_populates="cluster")
    observations = relationship("Observation", back_populates="cluster")
    gaps = relationship("Gap", back_populates="cluster")
    scores = relationship("ClusterScore", back_populates="cluster")
    activity_logs = relationship("ClusterActivityLog", back_populates="cluster")
    published_versions = relationship("PublishedVersion", back_populates="cluster")

    __table_args__ = (
        CheckConstraint("domain IN ('Universe', 'Earth', 'Human', 'Power', 'Tech', 'Culture')", name='chk_domain'),
        CheckConstraint("cluster_state IN ('Emerging', 'Active', 'Stabilizing', 'Disputed', 'Retracted')", name='chk_cluster_state'),
    )

class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(Integer, primary_key=True, index=True)
    raw_item_id = Column(Integer, ForeignKey("raw_items.item_id"))
    cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))
    level = Column(Integer, nullable=False)
    extract = Column(Text, nullable=False)
    pointer = Column(JSONB, nullable=False)
    reliability_score = Column(Float)
    extracted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    evidence_kind = Column(String(30), default='fact')

    raw_item = relationship("RawItem", back_populates="evidence")
    cluster = relationship("EventCluster", back_populates="evidence")

    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 5", name='chk_level'),
        CheckConstraint("evidence_kind IN ('fact', 'quote', 'data', 'inference')", name='chk_evidence_kind'),
        # Note: pointer structure checks are enforced by DB constraints in patch SQL or implementation logic
    )

class Observation(Base):
    __tablename__ = "observations"

    observation_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))
    observation_type = Column(String(50), nullable=False)
    state = Column(String(50), default='Active')
    content = Column(Text)
    payload = Column(JSONB)
    evidence_ids = Column(ARRAY(Integer))
    gap_ids = Column(ARRAY(Integer))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    cluster = relationship("EventCluster", back_populates="observations")

    __table_args__ = (
        CheckConstraint("observation_type IN ('hypothesis', 'prediction', 'constraint')", name='chk_observation_type'),
        CheckConstraint("state IN ('Active', 'Weakened', 'Falsified')", name='chk_obs_state'),
    )

class Gap(Base):
    __tablename__ = "gaps"

    gap_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))
    gap_level = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    needed_evidence_types = Column(ARRAY(Text))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    cluster = relationship("EventCluster", back_populates="gaps")

    __table_args__ = (
        CheckConstraint("gap_level IN ('low', 'mid', 'high', 'audit')", name='chk_gap_level'),
    )

class ClusterScore(Base):
    __tablename__ = "cluster_scores"

    score_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))
    consistency = Column(Float)
    mechanism_uncertainty = Column(Float)
    risk = Column(Float)
    contradiction_ratio = Column(Float)
    computed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    method_version = Column(String(50), default='governance_1.0')

    cluster = relationship("EventCluster", back_populates="scores")

class ClusterActivityLog(Base):
    __tablename__ = "cluster_activity_log"

    log_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))
    log_type = Column(String(50), nullable=False)
    log_data = Column(JSONB, nullable=False)
    logged_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    cluster = relationship("EventCluster", back_populates="activity_logs")

    __table_args__ = (
        CheckConstraint("log_type IN ('internal_tick', 'evidence_added', 'state_change', 'published', 'correction', 'retraction')", name='chk_log_type'),
    )

class PublishedVersion(Base):
    __tablename__ = "published_versions"

    version_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("event_clusters.cluster_id"))
    version_seq = Column(Integer, nullable=False)
    version_label = Column(String(20))
    published_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    reason = Column(String(255), nullable=False)
    changed_sections = Column(ARRAY(Text))
    added_evidence_ids = Column(ARRAY(Integer))
    score_delta = Column(JSONB)
    snapshot_payload = Column(JSONB, nullable=False)

    cluster = relationship("EventCluster", back_populates="published_versions")

    __table_args__ = (
        CheckConstraint("reason IN ('auto_60m', 'rapid_15m', 'active_30m', 'correction', 'retraction')", name='chk_reason'),
    )
