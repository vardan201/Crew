#!/usr/bin/env python
"""
Render.com deployment entry point
This file runs the FastAPI application from api.py
"""
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the FastAPI app from api.py
from api import app

# This is what uvicorn will look for
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
