#!/usr/bin/env python3
"""
Debug script to check sprint fetching
"""

import requests
import json

def debug_sprints():
    print("🔍 Debugging sprint fetching...")
    
    # Backend URL
    backend_url = "http://localhost:8000"
    
    # Check sprints endpoint
    try:
        print("📡 Calling /api/sprints...")
        sprints_response = requests.get(f"{backend_url}/api/sprints", timeout=30)
        print(f"Status Code: {sprints_response.status_code}")
        
        if sprints_response.status_code == 200:
            sprints_data = sprints_response.json()
            print(f"Response: {json.dumps(sprints_data, indent=2)}")
            
            if 'sprints' in sprints_data:
                print(f"📋 Found {len(sprints_data['sprints'])} sprints")
                for sprint in sprints_data['sprints']:
                    print(f"  - {sprint.get('name', 'Unknown')} (ID: {sprint.get('id', 'Unknown')}, State: {sprint.get('state', 'Unknown')})")
            else:
                print("❌ No 'sprints' key in response")
        else:
            print(f"❌ Error response: {sprints_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Also check the raw Jira connection
    print("\n🔍 Checking Jira connection...")
    try:
        # This would require the Jira credentials to be set up
        # For now, let's just check if the backend is properly connected
        print("Note: To debug Jira connection, you need to be logged in through the frontend first")
        
    except Exception as e:
        print(f"❌ Error checking Jira connection: {e}")

if __name__ == "__main__":
    debug_sprints() 