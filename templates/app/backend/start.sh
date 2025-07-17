#!/bin/bash
# Backend startup script for Company Task Management System

echo "🚀 Starting Flask Backend for Company Task Management System"
echo "============================================================"

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start the Flask development server
echo ""
echo "🌟 Starting Flask backend server..."
echo "📱 Backend API will be available at: http://localhost:5004"
echo "💻 Frontend PWA should be at: http://localhost:3000"
echo ""
echo "🔑 Demo login credentials:"
echo "   Username: admin | Password: admin123"
echo "   Username: user  | Password: user123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

python app.py
