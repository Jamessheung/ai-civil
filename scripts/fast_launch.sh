#!/bin/bash
echo "🚀 Initializing Fast Launch..."

# 1. Cleanup Ports
echo "🧹 Cleaning up ports 3001 & 8001..."
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# 2. Start Backend (Mock)
echo "🔌 Starting Mock API..."
cd backend
source venv/bin/activate
nohup uvicorn scripts.mock_api:app --reload --port 8001 > ../backend.log 2>&1 &
cd ..

# 3. Start Frontend
echo "⚛️ Starting Frontend..."
cd frontend
# Ensure dependencies are installed (fast check)
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies (first run)..."
    npm install
fi
PORT=3001 nohup npm run dev > ../frontend.log 2>&1 &
cd ..

# 4. Wait for Ready
echo "⏳ Waiting for server to be ready (this may take 10-20s)..."
count=0
while ! curl -s http://localhost:3001 > /dev/null; do
    sleep 1
    count=$((count+1))
    echo -n "."
    if [ $count -ge 60 ]; then
        echo "❌ Timeout waiting for frontend."
        exit 1
    fi
done

# 5. Launch
echo ""
echo "✅ System Online!"
open http://localhost:3001
