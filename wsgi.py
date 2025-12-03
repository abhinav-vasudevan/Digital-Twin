"""
WSGI configuration for PythonAnywhere deployment
This file wraps the FastAPI app for WSGI servers
"""
import sys
from pathlib import Path

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/Digital-Twin'  # Update this on PythonAnywhere
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the FastAPI app
from service.api import app

# Wrap FastAPI app for WSGI
application = app
