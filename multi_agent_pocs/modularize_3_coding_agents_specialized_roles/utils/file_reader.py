import os
from typing import Optional

class FileReader:
    """
    Utility class for reading files with path validation.
    Companion to FileWriter for the agentic system.
    """
    def __init__(self, base_dir: str = "."):
        self.base_dir = os.path.abspath(base_dir)

    def read(self, file_path: str) -> Optional[str]:
        """
        Reads content from the specified file path.
        Returns None if file doesn't exist or can't be read.
        """
        try:
            full_path = os.path.abspath(os.path.join(self.base_dir, file_path))
            
            # Security check: ensure we're reading within allowed paths
            if not full_path.startswith(self.base_dir):
                print(f"🚫 Security Alert: Attempted read outside base directory: {full_path}")
                return None

            if not os.path.exists(full_path):
                print(f"📄 File not found: {file_path}")
                return None
                
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            print(f"📖 FileReader: Read {file_path}")
            return content
            
        except Exception as e:
            print(f"❌ FileReader Error: {e}")
            return None

    def exists(self, file_path: str) -> bool:
        """Check if file exists."""
        try:
            full_path = os.path.abspath(os.path.join(self.base_dir, file_path))
            return os.path.exists(full_path)
        except:
            return False