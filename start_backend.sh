#!/bin/bash
# Quick start script for Neighborhood Sips application

echo "============================================================"
echo "Neighborhood Sips - Quick Start"
echo "============================================================"
echo ""

# Check if MongoDB is running
echo "Checking MongoDB..."
if command -v mongod &> /dev/null; then
    if pgrep -x "mongod" > /dev/null; then
        echo "✓ MongoDB is running"
    else
        echo "⚠ MongoDB is installed but not running"
        echo "  Please start MongoDB with: sudo service mongodb start"
        echo "  Or: mongod --dbpath /path/to/data"
    fi
else
    echo "⚠ MongoDB not found"
    echo "  Please install MongoDB from: https://www.mongodb.com/try/download/community"
fi

echo ""
echo "Starting Neighborhood Sips backend..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Load sample ingredients (if database is empty)
echo ""
echo "Checking for ingredients..."
python3 -c "
from pymongo import MongoClient
import sys
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['neighborhood_sips']
    count = db.ingredients.count_documents({})
    if count == 0:
        print('No ingredients found. Loading sample ingredients...')
        sys.exit(1)
    else:
        print(f'✓ Found {count} ingredients in database')
        sys.exit(0)
except Exception as e:
    print(f'⚠ Could not connect to MongoDB: {e}')
    sys.exit(0)
"

if [ $? -eq 1 ]; then
    python3 load_sample_ingredients.py
fi

echo ""
echo "============================================================"
echo "Starting Flask backend on http://localhost:5000"
echo "============================================================"
echo ""
echo "To access the frontend:"
echo "  1. Open another terminal"
echo "  2. cd backend/static"
echo "  3. python3 -m http.server 8000"
echo "  4. Open http://localhost:8000 in your browser"
echo ""
echo "Press Ctrl+C to stop the backend server"
echo ""

# Start the Flask application
python3 app.py
