#!/bin/bash
# Quick deployment script for PythonAnywhere
# Run this script on PythonAnywhere after uploading your code

set -e

echo "============================================================"
echo "Neighborhood Sips - PythonAnywhere Deployment Setup"
echo "============================================================"
echo ""

# Get PythonAnywhere username
if [ -z "$PYTHONANYWHERE_USERNAME" ]; then
    read -p "Enter your PythonAnywhere username: " PYTHONANYWHERE_USERNAME
fi

echo ""
echo "Setting up for user: $PYTHONANYWHERE_USERNAME"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ""
        echo "⚠ IMPORTANT: Edit the .env file with your MongoDB Atlas credentials!"
        echo ""
        echo "Run: nano .env"
        echo ""
        echo "Update the following:"
        echo "  - MONGO_URI: Your MongoDB Atlas connection string"
        echo "  - ALLOWED_ORIGINS: https://$PYTHONANYWHERE_USERNAME.pythonanywhere.com"
        echo ""
        read -p "Press Enter after you've updated the .env file..."
    else
        echo "Error: .env.example not found"
        exit 1
    fi
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo "Creating uploads directory..."
    mkdir -p uploads
    echo "✓ Uploads directory created"
fi

# Check if virtual environment exists
if [ -z "$VIRTUAL_ENV" ]; then
    echo ""
    echo "⚠ Virtual environment not activated!"
    echo ""
    echo "Please run these commands first:"
    echo "  mkvirtualenv --python=/usr/bin/python3.10 my_bar_env"
    echo "  workon my_bar_env"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "✓ Virtual environment activated: $VIRTUAL_ENV"
echo ""

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Test MongoDB connection
echo "Testing MongoDB connection..."
python3 << 'EOF'
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.environ.get('MONGO_URI')

if not mongo_uri or mongo_uri == 'mongodb://localhost:27017/':
    print("⚠ WARNING: MONGO_URI is not configured or still set to localhost")
    print("  Please update your .env file with MongoDB Atlas credentials")
    exit(1)

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✓ MongoDB connection successful!")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    print("  Please check your MONGO_URI in .env file")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "Please fix the MongoDB connection issue and run this script again."
    exit 1
fi

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure WSGI file in PythonAnywhere Web tab:"
echo "   - Path: /var/www/${PYTHONANYWHERE_USERNAME}_pythonanywhere_com_wsgi.py"
echo "   - Update with:"
echo ""
cat << 'WSGI_CONTENT'
import sys
import os

# Add your project directory to sys.path
path = '/home/USERNAME/my_bar/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set up environment variables
from dotenv import load_dotenv
env_path = os.path.join(path, '.env')
load_dotenv(env_path)

# Import Flask application
from app import app as application
WSGI_CONTENT

echo ""
echo "   (Replace USERNAME with your actual username: $PYTHONANYWHERE_USERNAME)"
echo ""
echo "2. Set virtual environment path in Web tab:"
echo "   /home/$PYTHONANYWHERE_USERNAME/.virtualenvs/my_bar_env"
echo ""
echo "3. Add static files mapping:"
echo "   URL: /api/uploads/"
echo "   Directory: /home/$PYTHONANYWHERE_USERNAME/my_bar/backend/uploads"
echo ""
echo "4. Click the 'Reload' button"
echo ""
echo "5. Test your API:"
echo "   https://$PYTHONANYWHERE_USERNAME.pythonanywhere.com/api/health"
echo ""
echo "6. (Optional) Load sample data:"
echo "   python3 load_sample_ingredients.py"
echo ""
