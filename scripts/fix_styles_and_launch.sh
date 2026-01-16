#!/bin/bash
echo "🎨 Starting UI Repair Sequence..."

# 1. Kill existing frontend
echo "🛑 Stopping current frontend..."
lsof -ti:3001 | xargs kill -9 2>/dev/null || true

# 2. Navigate to frontend
cd frontend

# 3. Deep Clean
echo "🧹 Deep cleaning build artifacts..."
rm -rf .next
rm -rf node_modules
rm -f package-lock.json

# 4. Re-install
echo "📦 Re-installing dependencies (this ensures tailwind/postcss matches)..."
npm install

# 5. Start Dev Server
echo "🚀 Launching Frontend..."
PORT=3001 nohup npm run dev > ../frontend_fix.log 2>&1 &

# 6. Wait for Ready
echo "⏳ Waiting for UI to hydrate..."
count=0
while ! curl -s http://localhost:3001 > /dev/null; do
    sleep 1
    count=$((count+1))
    echo -n "."
    if [ $count -ge 60 ]; then
        echo "❌ Startup timeout."
        exit 1
    fi
done

echo ""
echo "✅ UI Restored. Opening Browser..."
open http://localhost:3001
