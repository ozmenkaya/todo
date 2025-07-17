#!/bin/bash

echo "🚀 Deploying Company Task Management System"
echo "=========================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build new image
echo "🏗️ Building new image..."
docker-compose build --no-cache

# Start containers
echo "🚀 Starting containers..."
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for application to be ready..."
sleep 10

# Check health
echo "🔍 Checking application health..."
for i in {1..30}; do
    if curl -f http://localhost:5005/api/health > /dev/null 2>&1; then
        echo "✅ Application is healthy and ready!"
        echo "🌐 Access your application at: http://localhost:5005"
        echo "📱 The PWA should work on mobile devices too!"
        exit 0
    fi
    echo "⏳ Waiting for application... ($i/30)"
    sleep 2
done

echo "❌ Application failed to start properly"
echo "📋 Check logs with: docker-compose logs"
exit 1
