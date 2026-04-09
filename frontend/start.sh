#!/bin/bash

# Querify 2.0 - Frontend Server Startup
# 
# This script starts an HTTP server for the frontend
# Usage: ./start.sh [port]

PORT=${1:-8080}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

echo "🎨 Starting Querify Frontend"
echo "📍 Server: http://localhost:$PORT"
echo "🔗 Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 server.py "$PORT"
