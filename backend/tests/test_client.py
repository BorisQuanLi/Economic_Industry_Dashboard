import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from api.client import APIClient

# ...rest of existing test code...
