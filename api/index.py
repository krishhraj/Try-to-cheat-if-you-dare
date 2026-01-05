"""
Vercel Serverless Function Entrypoint for FastAPI Application

This file serves as the entry point for Vercel deployment.
It wraps the FastAPI application to work with Vercel's serverless functions.
"""

import sys
import os
from pathlib import Path

# Add the project root and backend directory to Python path
# In Vercel, the function root is at the project root
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

# Set up environment for backend imports
os.chdir(str(project_root))

# Import the FastAPI app
from backend.app.main import app

# For Vercel, export the ASGI app directly
# Vercel's @vercel/python builder supports ASGI applications natively
# The handler variable will be automatically detected
handler = app

