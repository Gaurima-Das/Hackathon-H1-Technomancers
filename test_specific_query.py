#!/usr/bin/env python3
"""
Test the specific JQL query that works in Jira
"""

from jira import JIRA
from datetime import datetime, timedelta

def test_specific_query():
    """Test the specific JQL query that works in Jira"""
    print("🧪 Testing Specific JQL Query")
    print("=" * 50)
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        # Test the exact query that works in Jira
        username = "parvesh.thapa@wideorbit.com"
        jql = f'worklogAuthor = "{username}" AND worklogDate >= "2024-03-19" ORDER BY created DESC'
        
        print(f"Testing JQL: {jql}")
        
        issues = jira.search_issues(jql, expand='worklog', maxResults=10)
        print(f"✅ Found {len(issues)} issues with worklogs")
        
        if len(issues) > 0:
            print("\n📋 Issues found:")
            for i, issue in enumerate(issues):
                print(f"   {i+1}. {issue.key}: {issue.fields.summary}")
                
                # Check worklogs for this issue
                if hasattr(issue.fields, 'worklog') and issue.fields.worklog:
                    worklogs = issue.fields.worklog.worklogs
                    print(f"      Worklogs: {len(worklogs)}")
                    for wl in worklogs[:3]:  # Show first 3 worklogs
                        if hasattr(wl, 'author') and wl.author:
                            author_name = getattr(wl.author, 'name', 'Unknown')
                            if author_name == username:
                                print(f"        - {wl.started}: {wl.timeSpent} ({wl.comment[:50]}...)")
        else:
            print("❌ No issues found with worklogs")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_different_date_formats():
    """Test different date formats for the same query"""
    print("\n\n📅 Testing Different Date Formats")
    print("=" * 50)
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        username = "parvesh.thapa@wideorbit.com"
        date_formats = [
            "2024-03-19",  # Date we know has worklogs
            "2024/03/19",  # With slashes
            "2024-01-01",  # Start of 2024
            "2020-01-01",  # Very old date
        ]
        
        for date_format in date_formats:
            print(f"\n🧪 Testing date: {date_format}")
            jql = f'worklogAuthor = "{username}" AND worklogDate >= "{date_format}" ORDER BY created DESC'
            print(f"   JQL: {jql}")
            
            try:
                issues = jira.search_issues(jql, expand='worklog', maxResults=5)
                print(f"   ✅ Found {len(issues)} issues")
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_specific_query()
    test_different_date_formats() 