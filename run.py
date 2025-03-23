"""
Application entry point

Run this script to start the application.
"""
import os
import sys
import logging

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import the application
try:
    logger.info(f"Python path: {sys.path}")
    
    # Try to import required modules first to catch import issues early
    logger.info("Checking module imports...")
    import flask
    logger.info("Flask imported successfully")
    
    # Create any missing directories that might be needed
    os.makedirs('backend/etl/transform/models/industry', exist_ok=True)
    os.makedirs('backend/etl/transform/adapters', exist_ok=True)
    os.makedirs('backend/etl/load/db/queries', exist_ok=True)
    
    # Now try to import and create the application
    try:
        from backend.webservice.factory import create_app
        logger.info("Factory module imported successfully")
        
        # Create the application
        app = create_app()
        logger.info("Application created successfully")
        
        if __name__ == '__main__':
            logger.info("Starting Economic Industry Dashboard application")
            port = int(os.environ.get('PORT', 5000))
            app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
        
except Exception as e:
    logger.error(f"Error starting application: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
