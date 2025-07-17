#!/bin/bash

# Production start script for Flask Backend
echo "🚀 Starting Flask Backend in Production Mode"
echo "============================================"

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Set production environment
export FLASK_ENV=production
export FLASK_APP=app.py

# Start the server
echo "🌟 Starting Flask backend server in production mode..."
echo "📱 Backend API will be available at: http://0.0.0.0:${PORT:-5005}"

gunicorn --bind 0.0.0.0:${PORT:-5005} --workers 4 --worker-class gthread --threads 2 app:app
