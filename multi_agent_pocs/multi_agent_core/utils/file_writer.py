import os
from typing import Optional

class FileWriter:
    """
    Utility class for handling file write operations with basic path validation.
    Acts as the 'Actuator' for the agentic system.
    """
    def __init__(self, base_dir: str = "."):
        self.base_dir = os.path.abspath(base_dir)

    def write(self, file_path: str, content: str) -> bool:
        """
        Writes content to the specified file path.
        """
        try:
            # Resolve full path
            full_path = os.path.abspath(os.path.join(self.base_dir, file_path))
            
            # Basic guardrail: Ensure we are writing within the project (or allowed paths)
            if not full_path.startswith(self.base_dir):
                print(f"🚫 Security Alert: Attempted write outside base directory: {full_path}")
                return False

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"💾 FileWriter: Persisted changes to {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ FileWriter Error: {e}")
            return False
