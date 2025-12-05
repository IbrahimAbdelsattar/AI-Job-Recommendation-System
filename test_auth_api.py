import requests
import uuid
import sys

BASE_URL = "http://localhost:5000/api/auth"

def test_signup_login():
    # Generate unique email
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    name = "Test User"
    
    print(f"Testing with email: {email}")
    
    # 1. Signup
    print("1. Testing Signup...")
    try:
        resp = requests.post(f"{BASE_URL}/signup", json={
            "email": email,
            "password": password,
            "full_name": name
        })
        print(f"Signup Status: {resp.status_code}")
        print(f"Signup Response: {resp.text}")
        
        if resp.status_code != 200:
            print("❌ Signup failed")
            return
    except Exception as e:
        print(f"❌ Signup request failed: {e}")
        return

    # 2. Login
    print("\n2. Testing Login...")
    try:
        resp = requests.post(f"{BASE_URL}/login", json={
            "email": email,
            "password": password
        })
        print(f"Login Status: {resp.status_code}")
        print(f"Login Response: {resp.text}")
        
        if resp.status_code == 200:
            print("✅ Login successful")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")

if __name__ == "__main__":
    test_signup_login()
