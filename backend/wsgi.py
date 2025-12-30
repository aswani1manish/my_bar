"""
WSGI entry point for PythonAnywhere deployment
This file is used by PythonAnywhere to run the Flask application
"""
import sys
import os

# Add your project directory to the sys.path
# On PythonAnywhere, this will be something like:
# /home/yourusername/my_bar/backend
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Import the Flask app
from app import app as application

# For debugging purposes (remove in production)
if __name__ == "__main__":
    application.run()
