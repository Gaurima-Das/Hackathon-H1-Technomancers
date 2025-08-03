#!/usr/bin/env python3
"""
Quick Start Script for Jira Management Dashboard
This script will install dependencies and start both backend and frontend
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def start_backend():
    """Start the backend server in a separate thread"""
    backend_script = os.path.join(os.path.dirname(__file__), 'start_backend.py')
    subprocess.run([sys.executable, backend_script])

def start_frontend():
    """Start the frontend server in a separate thread"""
    frontend_script = os.path.join(os.path.dirname(__file__), 'start_frontend.py')
    subprocess.run([sys.executable, frontend_script])

def main():
    print("🚀 Jira Management Dashboard - Quick Start")
    print("=" * 50)
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python installation"):
        print("❌ Python is not installed or not in PATH")
        return
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return
    
    print("\n🎯 Starting servers...")
    print("📝 Note: You'll need to open two terminal windows to run both servers")
    print("\nTerminal 1 - Backend:")
    print("python start_backend.py")
    print("\nTerminal 2 - Frontend:")
    print("python start_frontend.py")
    
    # Ask user if they want to start servers automatically
    response = input("\n🤔 Would you like to start the servers now? (y/n): ").lower()
    
    if response == 'y':
        print("\n🚀 Starting servers...")
        
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait a bit for backend to start
        time.sleep(3)
        
        # Start frontend in a separate thread
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        frontend_thread.start()
        
        # Wait a bit for frontend to start
        time.sleep(5)
        
        # Open browser
        try:
            webbrowser.open("http://localhost:8501")
            print("🌐 Opened dashboard in your browser")
        except:
            print("🌐 Please open http://localhost:8501 in your browser")
        
        print("\n⏳ Servers are running... Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down servers...")
    
    else:
        print("\n📋 Manual startup instructions:")
        print("1. Open Terminal 1 and run: python start_backend.py")
        print("2. Open Terminal 2 and run: python start_frontend.py")
        print("3. Open http://localhost:8501 in your browser")

if __name__ == "__main__":
    main() 