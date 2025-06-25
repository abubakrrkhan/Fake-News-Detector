#!/usr/bin/env python3
"""
Test script to verify that the Fake News Detection System is properly set up
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_module(module_name):
    """Check if a Python module is installed"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def main():
    # Print header
    print("\n=== Fake News Detection System Setup Test ===\n")
    
    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python version: {py_version}")
    if sys.version_info < (3, 8):
        print("[FAIL] Python 3.8+ required")
    else:
        print("[PASS] Python version requirement met")
    
    # Check core dependencies
    print("\nChecking core dependencies:")
    core_deps = [
        "fastapi", "uvicorn", "pydantic", "numpy", "pandas", 
        "nltk", "loguru", "dotenv", "requests"
    ]
    
    all_core_present = True
    for dep in core_deps:
        if check_module(dep):
            print(f"[PASS] {dep}")
        else:
            print(f"[FAIL] {dep} - missing")
            all_core_present = False
    
    # Check advanced dependencies
    print("\nChecking advanced dependencies (optional):")
    advanced_deps = [
        "torch", "tensorflow", "transformers", "spacy", 
        "googlesearch", "facenet_pytorch", "opencv"
    ]
    
    advanced_count = 0
    for dep in advanced_deps:
        if check_module(dep):
            print(f"[PASS] {dep}")
            advanced_count += 1
        else:
            print(f"[INFO] {dep} - not installed (optional)")
    
    # Check if files exist
    print("\nChecking project structure:")
    required_files = [
        "run.py", "requirements.txt", "dotenv.env",
        "app/main.py", "utils/sentiment_analyzer.py",
        "services/news_verification.py", "models/model_manager.py"
    ]
    
    all_files_present = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"[PASS] {file_path}")
        else:
            print(f"[FAIL] {file_path} - missing")
            all_files_present = False
    
    # Check logs directory
    if not Path("logs").exists():
        os.makedirs("logs", exist_ok=True)
        print("[PASS] logs directory created")
    else:
        print("[PASS] logs directory exists")
    
    # Print summary
    print("\n=== Summary ===")
    
    if all_core_present:
        print("[PASS] All core dependencies installed")
    else:
        print("[FAIL] Some core dependencies are missing - run: pip install -r requirements.txt")
    
    if advanced_count == 0:
        print("[INFO] No advanced dependencies detected - system will run in safe mode only")
    elif advanced_count < len(advanced_deps):
        print(f"[INFO] Some advanced dependencies detected ({advanced_count}/{len(advanced_deps)}) - limited advanced features")
    else:
        print("[PASS] All advanced dependencies installed - full functionality available")
    
    if all_files_present:
        print("[PASS] All required files present")
    else:
        print("[FAIL] Some required files are missing - check project structure")
    
    print("\n=== Running Options ===")
    print("Safe mode (basic features only):")
    print("  python run.py --safe-mode")
    print("\nMinimal mode (API endpoints only):")
    print("  python run.py --minimal")
    print("\nFull mode (requires advanced dependencies):")
    print("  python run.py")
    
if __name__ == "__main__":
    main() 