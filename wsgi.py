"""
WSGI configuration for PythonAnywhere deployment
This file wraps the FastAPI (ASGI) app for WSGI servers using a2wsgi
"""
import sys
from pathlib import Path

# Add your project directory to the sys.path
project_home = str(Path(__file__).parent.absolute())
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the FastAPI app
from service.api import app

# Wrap ASGI app (FastAPI) for WSGI using a2wsgi
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)
