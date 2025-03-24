"""
WSGI entry point for production deployments

This module provides a WSGI-compatible entry point for application servers
like Gunicorn, uWSGI, or mod_wsgi.

Example usage with Gunicorn:
    gunicorn wsgi:app -w 4 -b 0.0.0.0:5000
"""

import os
import sys
import logging

# Disable bytecode generation
sys.dont_write_bytecode = True

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the application factory
try:
    from backend.webservice.factory import create_app
    
    # Create the application
    app = create_app()
    logger.info("Application created successfully via WSGI")
    
except Exception as e:
    logger.error(f"Error creating application: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
