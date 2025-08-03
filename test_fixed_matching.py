#!/usr/bin/env python3
"""
Test the fixed assignee matching logic
"""

import sys
sys.path.append('backend')

from backend.app.services.jira_service import JiraService

def test_fixed_matching():
    print("🔍 Testing fixed assignee matching logic...")
    
    # Create Jira service instance
    jira_service = JiraService()
    
    # Test cases
    test_cases = [
        ("parvesh.thapa@wideorbit.com", "Parvesh Thapa (Contractor)"),
        ("mkumar@wideorbit.com", "Manish Kumar"),
        ("parvesh.thapa@wideorbit.com", "parvesh.thapa@wideorbit.com"),
        ("mkumar@wideorbit.com", "mkumar@wideorbit.com"),
    ]
    
    for username, assignee in test_cases:
        result = jira_service._match_assignee(username, assignee)
        print(f"Username: {username}")
        print(f"Assignee: {assignee}")
        print(f"Match: {result}")
        print("-" * 50)

if __name__ == "__main__":
    test_fixed_matching() 