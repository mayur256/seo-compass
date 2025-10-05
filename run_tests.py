#!/usr/bin/env python3
"""Test runner script for SEO Compass."""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("📤 STDOUT:")
        print(result.stdout)
    
    if result.stderr and result.returncode != 0:
        print("📥 STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"❌ {description} failed with return code {result.returncode}")
        return False
    else:
        print(f"✅ {description} passed")
        return True

def main():
    """Run all tests and validation checks."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("🚀 SEO Compass - Test & Validation Suite")
    print("==========================================")
    
    checks = [
        ("python3 -c \"from app.main import app; print('✅ FastAPI app imports successfully')\"", "App Import Test"),
        ("python3 -m pytest tests/test_health.py -v --tb=short", "Health Check Tests"),
        ("python3 -m pytest tests/test_analyze_flow.py -v --tb=short", "Analysis Flow Tests"),
        ("python3 -m pytest tests/services/ -v --tb=short", "Service Layer Tests"),
        ("python3 -m pytest tests/test_analysis_pipeline.py -v --tb=short", "Pipeline Integration Tests"),
        ("python3 -m pytest tests/test_analysis_endpoints.py -v --tb=short", "API Endpoint Tests"),
        ("python3 -m pytest tests/test_reports.py -v --tb=short", "Report & Download Tests"),
    ]
    
    passed_tests = 0
    total_tests = len(checks)
    
    for cmd, description in checks:
        if run_command(cmd, description):
            passed_tests += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! SEO Compass is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Start Redis: docker-compose up -d redis")
        print("   2. Start Celery: celery -A app.tasks.celery_app worker --loglevel=info")
        print("   3. Start API: uvicorn app.main:app --reload")
        print("   4. Visit: http://localhost:8000/docs")
        sys.exit(0)
    else:
        print(f"❌ {total_tests - passed_tests} tests failed!")
        print("\n🔧 Troubleshooting:")
        print("   - Check your .env configuration")
        print("   - Ensure all dependencies are installed: pip install -e .[dev]")
        print("   - Verify database connection")
        sys.exit(1)

if __name__ == "__main__":
    main()