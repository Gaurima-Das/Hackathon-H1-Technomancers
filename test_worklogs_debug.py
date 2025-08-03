#!/usr/bin/env python3
"""
Comprehensive worklogs debugging
"""

from jira import JIRA
from datetime import datetime, timedelta

def test_worklogs_without_date():
    """Test worklogs without date filter"""
    print("🔍 Testing Worklogs Without Date Filter")
    print("=" * 50)
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        # Test different username formats without date filter
        username_formats = [
            "parvesh.thapa@wideorbit.com",
            "parvesh.thapa",
            "parvesh_thapa",
            "parveshthapa"
        ]
        
        for username in username_formats:
            print(f"\n🧪 Testing username: {username}")
            jql = f'worklogAuthor = "{username}"'
            print(f"   JQL: {jql}")
            
            try:
                issues = jira.search_issues(jql, expand='worklog', maxResults=10)
                print(f"   ✅ Found {len(issues)} issues with worklogs")
                
                if len(issues) > 0:
                    print("   📋 Sample issues:")
                    for i, issue in enumerate(issues[:3]):
                        print(f"      {i+1}. {issue.key}: {issue.fields.summary}")
                        
                        # Show worklog details
                        if hasattr(issue.fields, 'worklog') and issue.fields.worklog:
                            worklogs = issue.fields.worklog.worklogs
                            print(f"         Worklogs: {len(worklogs)}")
                            for wl in worklogs[:2]:  # Show first 2 worklogs
                                if hasattr(wl, 'author') and wl.author:
                                    author_name = getattr(wl.author, 'name', 'Unknown')
                                    print(f"           - Author: {author_name}, Date: {wl.started}, Time: {wl.timeSpent}")
                                    
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_recent_dates():
    """Test with more recent dates"""
    print("\n\n📅 Testing Recent Dates")
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
        
        # Test with recent dates
        recent_dates = [
            "2025/01/01",  # January 1st, 2025
            "2024/12/01",  # December 1st, 2024
            "2024/11/01",  # November 1st, 2024
            "2024/01/01",  # January 1st, 2024
        ]
        
        for date in recent_dates:
            print(f"\n🧪 Testing date: {date}")
            jql = f'worklogAuthor = "{username}" AND worklogDate >= "{date}" ORDER BY created DESC'
            print(f"   JQL: {jql}")
            
            try:
                issues = jira.search_issues(jql, expand='worklog', maxResults=5)
                print(f"   ✅ Found {len(issues)} issues")
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_all_worklogs():
    """Test to find any worklogs at all"""
    print("\n\n🔍 Testing All Worklogs")
    print("=" * 50)
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        # Try to find any worklogs at all
        print("🧪 Searching for any worklogs...")
        jql = 'worklogDate IS NOT EMPTY'
        print(f"   JQL: {jql}")
        
        try:
            issues = jira.search_issues(jql, expand='worklog', maxResults=10)
            print(f"   ✅ Found {len(issues)} issues with any worklogs")
            
            if len(issues) > 0:
                print("   📋 Sample issues with worklogs:")
                for i, issue in enumerate(issues[:5]):
                    print(f"      {i+1}. {issue.key}: {issue.fields.summary}")
                    
                    if hasattr(issue.fields, 'worklog') and issue.fields.worklog:
                        worklogs = issue.fields.worklog.worklogs
                        print(f"         Total worklogs: {len(worklogs)}")
                        for wl in worklogs[:2]:
                            if hasattr(wl, 'author') and wl.author:
                                author_name = getattr(wl.author, 'name', 'Unknown')
                                print(f"           - Author: {author_name}, Date: {wl.started}")
                                
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_worklogs_without_date()
    test_recent_dates()
    test_all_worklogs() 