# AI Civilization News Observer (AI-Civil)

A "Civilization-Grade" news observation system based on Event Clusters, Evidence L5-L1, and Strict Governance.

**Repository**: [https://github.com/Jamessheung/ai-civil](https://github.com/Jamessheung/ai-civil)

## Project Overview

AI-Civil is an observational news engine that shifts the focus from "articles" to **Event Clusters**. It implements a strict evidence grading system (L5-L1) and a dual-lens observation mechanism (Observer vs Anthropic) to ensure auditability and reduce hallucination.

### Core Features
- **Event Cluster First**: Events are the atomic unit; articles are just rendering layers.
- **Evidence Governance**: L5 (Official/Auditable) to L1 (Inference) grading with strict pointers.
- **Strict Versioning**: Immutable `published_versions` with replay capabilities.
- **Dual-Lens**: Switch between *Observer* (Fact/Uncertainty) and *Anthropic* (Governance/Circuit) views.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+

### 1. Start Infrastructure
Start the PostgreSQL 15 database:
```bash
docker-compose up -d
```

### 2. Initialize Database (First Run Only)
The system requires a strictly governed schema with mandatory triggers.
```bash
# Enter the db container
docker exec -it ai_civilization_db psql -U ai_civ -d ai_civilization

# IN PSQL SHELL:
# \i /docker-entrypoint-initdb.d/schema.sql
# \i /docker-entrypoint-initdb.d/patch_v1_1_1.sql
```

### 3. Start Backend Services
The backend handles Data Ingestion, Evidence Extraction, and the 10-minute Heartbeat.
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Development Server
uvicorn main:app --reload --port 8000
```
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Local)

### 4. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
- **Web Interface**: [http://localhost:3000](http://localhost:3000) (Local)

## Architecture

- **Ingestor**: Fetches RSS feeds -> `raw_items` (Content Hash Dedup).
- **Evidence Extractor**: Processes content -> `evidence` (L5-L1 Rules).
- **Clusterer**: Groups evidence -> `event_clusters` (Domains: Universe, Earth, Human, Power, Tech, Culture).
- **Scorer**: Computes Consistency, Risk, and Structure metrics.
- **Heartbeat**: Orchestrates the pipeline (default: 10m interval).
- **Governance**: Database triggers ensure `last_updated_at` consistency and immutable logging.

## Verification

To verify the project structure and dependencies:
```bash
python scripts/verify_integrity.py
```

## License

MIT
