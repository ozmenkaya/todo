#!/bin/bash

echo "🏗️ Building Frontend for Production"
echo "=================================="

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build for production
echo "🔨 Building React app..."
npm run build

echo "✅ Frontend build completed!"
echo "📂 Build files are in the 'dist' directory"
