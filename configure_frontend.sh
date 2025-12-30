#!/bin/bash
# Configuration script for frontend deployment
# This script updates the API URL based on the deployment environment

set -e

echo "============================================================"
echo "Neighborhood Sips - Frontend Configuration"
echo "============================================================"
echo ""

# Check if API URL is provided as argument
if [ -z "$1" ]; then
    echo "Usage: ./configure_frontend.sh <API_URL>"
    echo ""
    echo "Examples:"
    echo "  Local:        ./configure_frontend.sh http://localhost:5000/api"
    echo "  PythonAnywhere: ./configure_frontend.sh https://yourusername.pythonanywhere.com/api"
    echo ""
    exit 1
fi

API_URL="$1"

# Navigate to frontend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

# Create config.js with the provided API URL
cat > js/config.js << EOF
// Configuration for Neighborhood Sips Application
// This file is generated during deployment
// Generated on: $(date)

// API Configuration
var APP_CONFIG = {
    apiUrl: '$API_URL'
};
EOF

echo "✓ Configuration updated successfully!"
echo ""
echo "API URL set to: $API_URL"
echo ""
echo "Configuration file: frontend/js/config.js"
echo ""
echo "To deploy to PythonAnywhere:"
echo "  1. Upload the entire 'frontend' directory to PythonAnywhere"
echo "  2. Set up a web app pointing to the 'frontend' directory"
echo "  3. The application will connect to: $API_URL"
echo ""
