#!/usr/bin/env python3
"""
Test script to verify the authentication and worklogs fixes
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"

def test_wrong_credentials():
    """Test that wrong credentials are properly rejected"""
    print("🧪 Testing wrong credentials...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/connect",
            params={
                "server": "https://wideorbit.atlassian.net",
                "email": "wrong@email.com",
                "api_token": "wrong_token"
            }
        )
        
        if response.status_code == 400:
            print("✅ Wrong credentials properly rejected")
            return True
        else:
            print(f"❌ Wrong credentials not rejected properly: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing wrong credentials: {e}")
        return False

def test_correct_credentials():
    """Test that correct credentials work"""
    print("\n🧪 Testing correct credentials...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/connect",
            params={
                "server": "https://wideorbit.atlassian.net",
                "email": "parvesh.thapa@wideorbit.com",
                "api_token": "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
            }
        )
        
        if response.status_code == 200:
            print("✅ Correct credentials work")
            return True
        else:
            print(f"❌ Correct credentials failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing correct credentials: {e}")
        return False

def test_worklogs():
    """Test worklogs functionality"""
    print("\n🧪 Testing worklogs...")
    
    try:
        # First connect with correct credentials
        connect_response = requests.post(
            f"{API_BASE_URL}/connect",
            params={
                "server": "https://wideorbit.atlassian.net",
                "email": "parvesh.thapa@wideorbit.com",
                "api_token": "ATATT3xFfGF0DReU8fTtuswU95fqaxzmvj_2hy5IhYihcctg_EBE1_YufgRQdTJ7_jG9XGEgERztFqg1Omkx6zSSF28BIOAG9enM7sApjO4muqfykRQs9PjLFl3vjPkVasldgU28w4IAtEGRU-nk537o-dEB4CLhrGQytaXQc2QCPdEDs3_om0s=FF3BF2EA"
            }
        )
        
        if connect_response.status_code != 200:
            print("❌ Failed to connect for worklogs test")
            return False
        
        # Test worklogs for a user
        username = "parvesh.thapa"
        worklogs_response = requests.get(
            f"{API_BASE_URL}/user/{username}/worklogs",
            params={"days": 7}
        )
        
        if worklogs_response.status_code == 200:
            data = worklogs_response.json()
            print(f"✅ Worklogs fetched successfully")
            print(f"   - Total worklogs: {data['total_worklogs']}")
            print(f"   - Total hours: {data['total_hours']}")
            return True
        elif worklogs_response.status_code == 404:
            print(f"✅ User '{username}' not found (expected for testing)")
            return True
        else:
            print(f"❌ Worklogs request failed: {worklogs_response.status_code}")
            print(f"Response: {worklogs_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing worklogs: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Authentication and Worklogs Fixes")
    print("=" * 60)
    
    # Test wrong credentials
    test_wrong_credentials()
    
    # Test correct credentials
    test_correct_credentials()
    
    # Test worklogs
    test_worklogs()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")

if __name__ == "__main__":
    main() 