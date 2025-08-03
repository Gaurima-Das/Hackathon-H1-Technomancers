#!/usr/bin/env python3
"""
Debug script to test different username formats and date formats
"""

from jira import JIRA
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_different_usernames():
    """Test different username formats"""
    print("🔍 Testing Different Username Formats")
    print("=" * 50)
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        # Test different username formats
        username_formats = [
            "parvesh.thapa",
            "parvesh.thapa@wideorbit.com", 
            "parvesh_thapa",
            "parveshthapa",
            "Parvesh.Thapa",
            "PARVESH.THAPA"
        ]
        
        for username in username_formats:
            print(f"\n🧪 Testing username: {username}")
            
            # Test 1: Check if user exists
            try:
                jql = f'assignee = "{username}"'
                issues = jira.search_issues(jql, maxResults=1)
                print(f"   ✅ User exists (found {len(issues)} assigned issues)")
            except Exception as e:
                print(f"   ❌ User not found: {str(e)[:100]}")
            
            # Test 2: Check worklogs
            try:
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                jql = f'worklogAuthor = "{username}" AND worklogDate >= "{start_date}"'
                issues = jira.search_issues(jql, maxResults=5)
                print(f"   ✅ Worklogs query works (found {len(issues)} issues with worklogs)")
            except Exception as e:
                print(f"   ❌ Worklogs query failed: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def test_date_formats():
    """Test different date formats"""
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
        
        # Test different date formats - prioritize the correct Jira format
        date_formats = [
            (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d'),  # 2025/01/26 (CORRECT)
            (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # 2025-01-26
            (datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y'),  # 26/01/2025
            (datetime.now() - timedelta(days=7)).strftime('%m/%d/%Y'),  # 01/26/2025
        ]
        
        username = "parvesh.thapa"  # Use the most likely format
        
        for date_format in date_formats:
            print(f"\n🧪 Testing date format: {date_format}")
            
            try:
                jql = f'worklogAuthor = "{username}" AND worklogDate >= "{date_format}"'
                print(f"   JQL: {jql}")
                issues = jira.search_issues(jql, maxResults=5)
                print(f"   ✅ Found {len(issues)} issues with worklogs")
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def test_simple_worklog_search():
    """Test a simple worklog search without date filter"""
    print("\n\n🔍 Testing Simple Worklog Search")
    print("=" * 50)
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        # Test simple worklog search
        username_formats = ["parvesh.thapa", "parvesh.thapa@wideorbit.com"]
        
        for username in username_formats:
            print(f"\n🧪 Testing simple worklog search for: {username}")
            
            try:
                jql = f'worklogAuthor = "{username}"'
                print(f"   JQL: {jql}")
                issues = jira.search_issues(jql, maxResults=10)
                print(f"   ✅ Found {len(issues)} issues with worklogs")
                
                if len(issues) > 0:
                    print("   📋 Sample issues:")
                    for i, issue in enumerate(issues[:3]):
                        print(f"      {i+1}. {issue.key}: {issue.fields.summary}")
                        
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}")

if __name__ == "__main__":
    test_different_usernames()
    test_date_formats()
    test_simple_worklog_search() 