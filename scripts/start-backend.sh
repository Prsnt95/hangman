#!/bin/bash

echo "⚡ Starting FastAPI Backend..."
echo "=============================="

cd /workspace

echo "🔧 Starting uvicorn server on 0.0.0.0:8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload