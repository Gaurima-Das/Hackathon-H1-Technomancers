#!/usr/bin/env python3
"""
Debug script to test Jira authentication directly
"""

from jira import JIRA
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_jira_connection():
    """Test Jira connection directly"""
    print("🔍 Debugging Jira Authentication")
    print("=" * 50)
    
    # Get credentials from environment
    server = os.getenv("JIRA_SERVER", "https://wideorbit.atlassian.net")
    email = os.getenv("JIRA_EMAIL", "parvesh.thapa@wideorbit.com")
    api_token = os.getenv("JIRA_API_TOKEN", "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA")
    
    print(f"Server: {server}")
    print(f"Email: {email}")
    print(f"API Token (first 20 chars): {api_token[:20]}...")
    print(f"API Token length: {len(api_token)}")
    
    try:
        print("\n🔄 Creating JIRA object...")
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        print("✅ JIRA object created successfully")
        
        print("\n🔄 Testing authentication with myself()...")
        myself = jira.myself()
        print(f"✅ Authentication successful!")
        print(f"   User: {myself.displayName}")
        print(f"   Email: {myself.emailAddress}")
        print(f"   Active: {myself.active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_simple_connection():
    """Test a simpler connection approach"""
    print("\n🔄 Testing simple connection...")
    
    server = "https://wideorbit.atlassian.net"
    email = "parvesh.thapa@wideorbit.com"
    api_token = "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
    
    try:
        jira = JIRA(
            server=server,
            basic_auth=(email, api_token)
        )
        
        # Try a simple search instead of myself()
        issues = jira.search_issues('project = "TEST"', maxResults=1)
        print("✅ Simple connection test successful")
        return True
        
    except Exception as e:
        print(f"❌ Simple connection failed: {e}")
        return False

if __name__ == "__main__":
    test_jira_connection()
    test_simple_connection() 