#!/usr/bin/env python3

import os
import ast
import hashlib
import chardet
from pathlib import Path

def check_python_syntax(file_path):
    """Check if file contains valid Python syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

def check_file_encoding(file_path):
    """Detect file encoding and check for corruption"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            print(f"File: {file_path}")
            print(f"Encoding: {result['encoding']}")
            print(f"Confidence: {result['confidence']}")
            return result['confidence'] > 0.9
    except Exception as e:
        print(f"Error checking encoding for {file_path}: {e}")
        return False

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def main():
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))
    
    for file_path in python_files:
        print(f"\nChecking {file_path}:")
        print("-" * 50)
        
        # Check syntax
        syntax_valid = check_python_syntax(file_path)
        print(f"Syntax valid: {syntax_valid}")
        
        # Check encoding
        encoding_valid = check_file_encoding(file_path)
        print(f"Encoding valid: {encoding_valid}")
        
        # Calculate hash
        file_hash = calculate_file_hash(file_path)
        print(f"File hash: {file_hash}")

if __name__ == "__main__":
    main()
