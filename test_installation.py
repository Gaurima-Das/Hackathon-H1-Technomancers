#!/usr/bin/env python3
"""
Test script to verify Jira Management Dashboard installation
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def main():
    print("🧪 Testing Jira Management Dashboard Installation")
    print("=" * 50)
    
    # Test backend dependencies
    print("\n📦 Backend Dependencies:")
    backend_deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("jira", "Jira"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("python-dotenv", "Python-dotenv"),
        ("pandas", "Pandas"),
        ("plotly", "Plotly")
    ]
    
    backend_success = 0
    for module, name in backend_deps:
        if test_import(module, name):
            backend_success += 1
    
    # Test frontend dependencies
    print("\n🎨 Frontend Dependencies:")
    frontend_deps = [
        ("streamlit", "Streamlit"),
        ("requests", "Requests"),
        ("plotly", "Plotly (Frontend)")
    ]
    
    frontend_success = 0
    for module, name in frontend_deps:
        if test_import(module, name):
            frontend_success += 1
    
    # Summary
    print("\n📊 Summary:")
    print(f"Backend: {backend_success}/{len(backend_deps)} dependencies installed")
    print(f"Frontend: {frontend_success}/{len(frontend_deps)} dependencies installed")
    
    total_deps = len(backend_deps) + len(frontend_deps)
    total_success = backend_success + frontend_success
    
    if total_success == total_deps:
        print(f"\n🎉 All {total_deps} dependencies are installed correctly!")
        print("✅ You can now run the application using:")
        print("   python quick_start.py")
    else:
        print(f"\n⚠️  {total_deps - total_success} dependencies are missing.")
        print("Please run: pip install -r requirements.txt")
    
    # Test Python version
    print(f"\n🐍 Python Version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✅ Python version is compatible")
    else:
        print("❌ Python 3.8+ is required")

if __name__ == "__main__":
    main() 