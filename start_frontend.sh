#!/bin/bash
# Start frontend server for Neighborhood Sips

echo "============================================================"
echo "Neighborhood Sips - Frontend Server"
echo "============================================================"
echo ""

cd "$(dirname "$0")/backend/static"

echo "Starting frontend server on http://localhost:8000"
echo ""
echo "Open your browser and navigate to:"
echo "  http://localhost:8000"
echo ""
echo "Make sure the backend is running on http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8000
