#!/bin/bash

# Exit on error
set -e

echo "=== STARTING AI CIVILIZATION DEMO ==="

# 1. Start Database
echo "[1] Starting Database..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

# Wait for DB
echo "Waiting for DB to accept connections..."
sleep 5

# 2. Setup Backend & Seed
echo "[2] Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Seed Data (using venv python)
echo "[3] Seeding Data..."
./backend/venv/bin/python3 scripts/seed_data.py

# 3. Start Backend
echo "[4] Starting API Server..."
cd backend
./venv/bin/uvicorn main:app --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID)"
cd ..

# 4. Start Frontend
echo "[5] Starting Frontend..."
cd frontend
npm install
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend running (PID: $FRONTEND_PID)"
cd ..

echo "=== SYSTEM ONLINE ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "PIDs: API=$BACKEND_PID, UI=$FRONTEND_PID"

# Wait loop
wait $BACKEND_PID $FRONTEND_PID
