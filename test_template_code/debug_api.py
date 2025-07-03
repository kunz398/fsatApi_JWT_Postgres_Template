#!/usr/bin/env python3
"""
Debug script to test API endpoints directly
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing API endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test registration
    test_user = {
        "username": "debuguser",
        "email": "debug@test.com",
        "password": "debugpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        print(f"Registration: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Registration failed: {e}")
    
    # Test login
    try:
        response = requests.post(f"{base_url}/api/auth/login", data={
            "username": "debuguser",
            "password": "debugpass123"
        })
        print(f"Login: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            tokens = response.json()
            access_token = tokens.get("access_token")
            
            # Test items endpoint
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{base_url}/api/items/", headers=headers)
            print(f"Items GET: {response.status_code} - {response.json()}")
            
            # Create a test item
            test_item = {
                "title": "Debug Test Item",
                "description": "This is a test item created by debug script"
            }
            response = requests.post(f"{base_url}/api/items/", json=test_item, headers=headers)
            print(f"Item creation: {response.status_code} - {response.json()}")
            
            # Get items again
            response = requests.get(f"{base_url}/api/items/", headers=headers)
            print(f"Items GET (after creation): {response.status_code} - {response.json()}")
            
    except Exception as e:
        print(f"Login/Items test failed: {e}")

if __name__ == "__main__":
    test_api() 