"""Common imports and utilities used across the application."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def setup_project_path():
    """Add project root to Python path"""
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

def get_environment() -> str:
    """Get current environment"""
    return os.getenv('APP_ENV', 'local')
