#!/usr/bin/env python3
"""
Debug script to check ticket DX-2210 status
"""

import requests
import json

def debug_ticket():
    print("🔍 Debugging ticket DX-2210...")
    
    # Backend URL
    backend_url = "http://localhost:8000"
    
    # First, check if backend is running
    try:
        health_response = requests.get(f"{backend_url}/api/health", timeout=10)
        if health_response.status_code != 200:
            print("❌ Backend is not responding properly")
            return
        print("✅ Backend is running")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Get all sprints
    try:
        sprints_response = requests.get(f"{backend_url}/api/sprints", timeout=30)
        if sprints_response.status_code == 200:
            sprints_data = sprints_response.json()
            print(f"📋 Found {len(sprints_data.get('sprints', []))} sprints")
            
            # Check each sprint for DX-2210
            for sprint in sprints_data.get('sprints', []):
                sprint_id = sprint.get('id')
                sprint_name = sprint.get('name')
                sprint_state = sprint.get('state')
                
                print(f"\n🔍 Checking sprint: {sprint_name} (ID: {sprint_id}, State: {sprint_state})")
                
                # Get sprint report
                try:
                    report_response = requests.get(f"{backend_url}/api/sprint/{sprint_id}/report", timeout=30)
                    if report_response.status_code == 200:
                        report_data = report_response.json()
                        issues = report_data.get('issues', [])
                        
                        # Look for DX-2210
                        for issue in issues:
                            if issue.get('key') == 'DX-2210':
                                print(f"✅ Found DX-2210 in sprint {sprint_name}!")
                                print(f"   Assignee: {issue.get('assignee', 'Unassigned')}")
                                print(f"   Status: {issue.get('status', 'Unknown')}")
                                print(f"   Priority: {issue.get('priority', 'Unknown')}")
                                print(f"   Story Points: {issue.get('story_points', 'None')}")
                                return
                        
                        print(f"   ❌ DX-2210 not found in this sprint ({len(issues)} issues checked)")
                    else:
                        print(f"   ❌ Failed to get sprint report: {report_response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error getting sprint report: {e}")
        else:
            print(f"❌ Failed to get sprints: {sprints_response.status_code}")
    except Exception as e:
        print(f"❌ Error getting sprints: {e}")
    
    print("\n❌ DX-2210 not found in any sprint")
    print("\n💡 Possible reasons:")
    print("   - Ticket is not assigned to any sprint")
    print("   - Ticket is in a sprint that's not active")
    print("   - Ticket might be in a different project")
    print("   - Backend filtering logic might be excluding it")

if __name__ == "__main__":
    debug_ticket() 