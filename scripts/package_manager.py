import pkg_resources
import sys
import subprocess
from typing import List

def clean_requirement(req: str) -> str:
    """Clean requirement string to get just the package name."""
    parts = req.split('#')[0].strip()
    for op in ['>=', '==', '<']:
        parts = parts.split(op)[0]
    return parts.strip()

def get_requirements() -> List[str]:
    """Get all requirements from both backend and frontend."""
    requirements = []
    for req_file in ['backend/requirements.txt', 'frontend/requirements.txt']:
        try:
            with open(req_file) as f:
                requirements.extend([
                    l.strip() for l in f.readlines()
                    if l.strip() and not l.startswith('#')
                ])
        except FileNotFoundError:
            print(f"Warning: {req_file} not found")
    return requirements

def verify_packages():
    """Verify all required packages are installed."""
    required = [clean_requirement(r) for r in get_requirements()]
    required = list(set([r for r in required if r]))
    installed = [p.key for p in pkg_resources.working_set]
    
    missing = [p for p in required if p.lower() not in [x.lower() for x in installed]]
    
    if missing:
        print("Missing packages: " + ", ".join(missing))
        sys.exit(1)
    print("All packages installed!")
    sys.exit(0)

def install_missing():
    """Install any missing packages."""
    required = get_requirements()
    installed = [p.key for p in pkg_resources.working_set]
    missing = [p for p in required if clean_requirement(p).lower() not in [x.lower() for x in installed]]
    
    if missing:
        print("Installing missing packages: " + ", ".join(missing))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir"] + missing)
    else:
        print("All packages already installed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_missing()
    else:
        verify_packages()
