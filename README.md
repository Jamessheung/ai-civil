# AI Civilization News Observer (v1.1.1)

A "Civilization-Grade" news observation system based on Event Clusters, Evidence L5-L1, and Strict Governance.

## Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Node.js 18+

## Quick Start (Sprint 1)

### 1. Start Database
```bash
docker-compose up -d
```
Verified PostgreSQL 15 will start on port 5432.

### 2. Initialize Schema & Patches
**CRITICAL**: You must execute the schema and the mandatory patch block.
```bash
# Enter the db container
docker exec -it ai_civilization_db psql -U ai_civ -d ai_civilization

# IN PSQL SHELL:
# \i /docker-entrypoint-initdb.d/schema.sql
# \i /docker-entrypoint-initdb.d/patch_v1_1_1.sql
```
(Alternatively, if you restart the container with empty data, it might auto-init using the files in /docker-entrypoint-initdb.d if mapped correctly.)

### 3. Start Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Server (Development)
uvicorn main:app --reload --port 8000
```
Swagger UI: http://localhost:8000/docs

### 4. Start Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Frontend: http://localhost:3000

## Architecture

- **Ingestor**: Fetches RSS -> `raw_items` (Deduped).
- **Evidence Extractor**: `raw_items` -> `evidence` (L5-L1 Logic).
- **Clusterer**: Groups evidence into `event_clusters` (Domain: Universe/Earth/Human/Power/Tech/Culture).
- **Scorer**: Calculates Risk/Consistency.
- **Heartbeat**: orchestrates the pipeline every 10m.
- **Governance**: strict strict `last_updated_at` triggers and `log_data` schemas.

## Verification
Run integrity check:
```bash
python scripts/verify_integrity.py
```
