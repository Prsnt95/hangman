#!/bin/bash

echo "🚀 Starting React Frontend..."
echo "================================"

cd /workspace/frontend

# Check if node_modules exists, if not install dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🌐 Starting React development server on 0.0.0.0:3000..."
HOST=0.0.0.0 npm start
