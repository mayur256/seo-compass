#!/usr/bin/env python3
"""Setup validation script for SEO Compass."""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description} - Found")
        return True
    else:
        print(f"❌ {description} - Missing: {filepath}")
        return False

def check_env_file():
    """Check .env file configuration."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file - Missing (copy from .env.example)")
        return False
    
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL", 
        "CELERY_BROKER_URL",
        "CELERY_RESULT_BACKEND",
        "SECRET_KEY"
    ]
    
    with open(env_path) as f:
        content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ .env configuration - Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ .env configuration - OK")
        return True

def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import fastapi
        import sqlalchemy
        import celery
        import redis
        import pydantic
        import httpx
        import bs4
        print("✅ Core dependencies - Installed")
        return True
    except ImportError as e:
        print(f"❌ Dependencies - Missing: {e}")
        print("   Run: pip install -e .[dev]")
        return False

def check_docker():
    """Check Docker availability."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker - Available")
            return True
        else:
            print("❌ Docker - Not available")
            return False
    except FileNotFoundError:
        print("❌ Docker - Not installed")
        return False

def check_redis_connection():
    """Check Redis connection."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection - OK")
        return True
    except Exception as e:
        print(f"❌ Redis connection - Failed: {e}")
        print("   Start Redis: docker-compose up -d redis")
        return False

def main():
    """Run all validation checks."""
    print("🧭 SEO Compass - Setup Validation")
    print("=" * 40)
    
    checks = [
        (check_python_version, "Python Version"),
        (lambda: check_file_exists("pyproject.toml", "Project Configuration"), "Project Files"),
        (lambda: check_file_exists("app/main.py", "Main Application"), "App Structure"),
        (check_env_file, "Environment Configuration"),
        (check_dependencies, "Python Dependencies"),
        (check_docker, "Docker"),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_func, description in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {description} - Error: {e}")
    
    print(f"\n📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Setup validation successful!")
        print("\n🚀 Next steps:")
        print("   1. Start Redis: docker-compose up -d redis")
        print("   2. Run tests: python run_tests.py")
        print("   3. Start services:")
        print("      - Celery: celery -A app.tasks.celery_app worker --loglevel=info")
        print("      - API: uvicorn app.main:app --reload")
        print("   4. Visit: http://localhost:8000/docs")
    else:
        print(f"\n❌ {total - passed} validation checks failed!")
        print("\n🔧 Fix the issues above and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()