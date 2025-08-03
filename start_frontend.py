#!/usr/bin/env python3
"""
Startup script for Jira Management Dashboard Frontend
"""

import subprocess
import sys
import os

def main():
    print("🎨 Starting Jira Management Dashboard Frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("🔗 Make sure the backend is running at http://localhost:8000")
    print("\nPress Ctrl+C to stop the server")
    
    # Change to frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    os.chdir(frontend_dir)
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 