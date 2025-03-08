#!/usr/bin/env python3
"""
Package Management Utility

Usage:
    python3 scripts/package_manager.py --sync    # Sync package versions
    python3 scripts/package_manager.py --install # Install missing packages
    python3 scripts/package_manager.py          # Verify packages

When to use:
1. After adding new dependencies to root requirements.txt
2. Before starting development in a new environment
3. When syncing dependencies across team members
"""
import argparse
import pkg_resources
import sys
import subprocess
from pathlib import Path
from typing import List

def clean_requirement(req: str) -> str:
    """Clean requirement string to get just the package name."""
    parts = req.split('#')[0].strip()
    for op in ['>=', '==', '<']:
        parts = parts.split(op)[0]
    return parts.strip()

def get_requirements() -> List[str]:
    """Get all requirements from both backend and frontend."""
    root_dir = Path(__file__).parent.parent
    requirements = []
    for req_file in ['backend/requirements.txt', 'frontend/requirements.txt']:
        try:
            with open(root_dir / req_file) as f:
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

def sync_requirements():
    """Synchronize package versions between root and component requirements."""
    root_dir = Path(__file__).parent.parent
    root_reqs = (root_dir / 'requirements.txt').read_text().splitlines()
    versions = {line.split('==')[0]: line for line in root_reqs 
               if '==' in line and not line.startswith('#')}
    
    for component in ['backend', 'frontend']:
        req_file = root_dir / component / 'requirements.txt'
        if req_file.exists():
            component_reqs = req_file.read_text().splitlines()
            updated_reqs = [
                versions.get(line.split('==')[0], line)
                if '==' in line and not line.startswith('#')
                else line
                for line in component_reqs
            ]
            req_file.write_text('\n'.join(updated_reqs))
            print(f"Updated {component}/requirements.txt")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Package management utilities')
    parser.add_argument('--sync', action='store_true', help='Synchronize requirements')
    parser.add_argument('--install', action='store_true', help='Install missing packages')
    args = parser.parse_args()
    
    if args.sync:
        sync_requirements()
    elif args.install:
        install_missing()
    else:
        verify_packages()
