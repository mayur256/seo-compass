#!/usr/bin/env python3
"""Test runner script for SEO Compass."""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*50)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} passed")
        return True

def main():
    """Run all tests and checks."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    checks = [
        ("python -m pytest tests/test_health.py -v", "Health Check Tests"),
        ("python -m pytest tests/test_analyze_flow.py -v", "Analysis Flow Tests"),
        ("python -m pytest tests/services/ -v", "Service Tests"),
        ("python -m pytest tests/test_analysis_pipeline.py -v", "Pipeline Integration Tests"),
        ("python -c \"from app.main import app; print('✅ App imports successfully')\"", "App Import Test"),
    ]
    
    all_passed = True
    
    for cmd, description in checks:
        if not run_command(cmd, description):
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()