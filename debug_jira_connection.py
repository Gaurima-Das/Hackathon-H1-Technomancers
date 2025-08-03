#!/usr/bin/env python3
"""
Debug script to test Jira connection and sprint fetching
"""

import requests
import json

def debug_jira_connection():
    print("🔍 Debugging Jira connection and sprint fetching...")
    
    # Backend URL
    backend_url = "http://localhost:8000"
    
    # First, try to connect to Jira
    print("🔗 Attempting to connect to Jira...")
    try:
        connect_data = {
            "server": "https://wideorbit.atlassian.net",
            "email": "parvesh.thapa@wideorbit.com",
            "api_token": "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9jLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
        }
        
        connect_response = requests.post(
            f"{backend_url}/api/connect",
            params=connect_data,
            timeout=30
        )
        
        print(f"Connect Status: {connect_response.status_code}")
        if connect_response.status_code == 200:
            print("✅ Jira connection successful")
            print(f"Response: {connect_response.json()}")
        else:
            print(f"❌ Jira connection failed: {connect_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error connecting to Jira: {e}")
        return
    
    # Now try to get sprints
    print("\n📋 Fetching sprints...")
    try:
        sprints_response = requests.get(f"{backend_url}/api/sprints", timeout=30)
        print(f"Sprints Status: {sprints_response.status_code}")
        
        if sprints_response.status_code == 200:
            sprints_data = sprints_response.json()
            print(f"Sprints Response: {json.dumps(sprints_data, indent=2)}")
            
            if 'sprints' in sprints_data and sprints_data['sprints']:
                print(f"✅ Found {len(sprints_data['sprints'])} sprints")
                for sprint in sprints_data['sprints']:
                    print(f"  - {sprint.get('name', 'Unknown')} (ID: {sprint.get('id', 'Unknown')}, State: {sprint.get('state', 'Unknown')})")
            else:
                print("❌ No sprints found")
        else:
            print(f"❌ Failed to get sprints: {sprints_response.text}")
            
    except Exception as e:
        print(f"❌ Error getting sprints: {e}")

if __name__ == "__main__":
    debug_jira_connection() 