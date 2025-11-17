#!/usr/bin/env python3
"""
Authentication Testing Script
Tests registration, login, token validation, and logout functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_auth_flow():
    """Test complete authentication flow"""
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 60)

    # Test 1: Register with weak password (should fail)
    print("\n1. Testing registration with weak password...")
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "weak",  # Too short, no uppercase, no numbers
        "first_name": "Test",
        "last_name": "User"
    })

    if response.status_code == 400:
        print("   ✓ Weak password correctly rejected")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"   ✗ FAILED: Expected 400, got {response.status_code}")
        return False

    # Test 2: Register with strong password (should succeed)
    print("\n2. Testing registration with strong password...")
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongPass123",  # Meets all requirements
        "first_name": "Test",
        "last_name": "User"
    })

    if response.status_code == 201:
        data = response.json()
        token1 = data.get('token')
        print("   ✓ Registration successful")
        print(f"   User: {data['user']['email']} (Role: {data['user']['role']})")
        print(f"   Token: {token1[:20]}...")
    else:
        print(f"   ✗ FAILED: Expected 201, got {response.status_code}")
        print(f"   Response: {response.json()}")
        return False

    # Test 3: Duplicate registration (should fail)
    print("\n3. Testing duplicate email registration...")
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser2",
        "password": "StrongPass123",
        "first_name": "Test",
        "last_name": "User"
    })

    if response.status_code == 409:
        print("   ✓ Duplicate email correctly rejected")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"   ✗ FAILED: Expected 409, got {response.status_code}")
        return False

    # Test 4: Login with correct credentials
    print("\n4. Testing login with correct credentials...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "StrongPass123"
    })

    if response.status_code == 200:
        data = response.json()
        token2 = data.get('token')
        print("   ✓ Login successful")
        print(f"   Token: {token2[:20]}...")
    else:
        print(f"   ✗ FAILED: Expected 200, got {response.status_code}")
        print(f"   Response: {response.json()}")
        return False

    # Test 5: Login with wrong password
    print("\n5. Testing login with wrong password...")
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword123"
    })

    if response.status_code == 401:
        print("   ✓ Invalid credentials correctly rejected")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"   ✗ FAILED: Expected 401, got {response.status_code}")
        return False

    # Test 6: Access protected endpoint with valid token
    print("\n6. Testing access to protected endpoint with valid token...")
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token2}"}
    )

    if response.status_code == 200:
        data = response.json()
        print("   ✓ Protected endpoint access successful")
        print(f"   User data: {data['email']} - {data['first_name']} {data['last_name']}")
    else:
        print(f"   ✗ FAILED: Expected 200, got {response.status_code}")
        print(f"   Response: {response.json()}")
        return False

    # Test 7: Access without token
    print("\n7. Testing access to protected endpoint without token...")
    response = requests.get(f"{BASE_URL}/api/auth/me")

    if response.status_code == 401:
        print("   ✓ Access correctly denied without token")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"   ✗ FAILED: Expected 401, got {response.status_code}")
        return False

    # Test 8: Logout (blacklist token)
    print("\n8. Testing logout functionality...")
    response = requests.post(
        f"{BASE_URL}/api/auth/logout",
        headers={"Authorization": f"Bearer {token2}"}
    )

    if response.status_code == 200:
        print("   ✓ Logout successful")
        print(f"   Message: {response.json().get('message')}")
    else:
        print(f"   ✗ FAILED: Expected 200, got {response.status_code}")
        print(f"   Response: {response.json()}")
        return False

    # Test 9: Try to use blacklisted token
    print("\n9. Testing access with blacklisted token...")
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token2}"}
    )

    if response.status_code == 401:
        print("   ✓ Blacklisted token correctly rejected")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"   ✗ FAILED: Expected 401, got {response.status_code}")
        print(f"   Response: {response.json()}")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_auth_flow()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to server at", BASE_URL)
        print("Make sure the Flask server is running with: python crm_app.py")
        sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
