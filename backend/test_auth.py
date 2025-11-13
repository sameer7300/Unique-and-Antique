#!/usr/bin/env python
"""
Quick test script to verify authentication endpoints are working.
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import User

def test_backend_auth():
    """Test the authentication endpoints directly."""
    
    base_url = 'http://127.0.0.1:8000/api'
    
    # Test data
    test_user_data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpassword123',
        'password_confirm': 'testpassword123'
    }
    
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    
    print("Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test 1: Create a test user directly in database
    print("1. Creating test user in database...")
    try:
        # Delete existing user if exists
        User.objects.filter(email=test_user_data['email']).delete()
        
        # Create new user
        user = User.objects.create_user(
            email=test_user_data['email'],
            username=test_user_data['username'],
            first_name=test_user_data['first_name'],
            last_name=test_user_data['last_name'],
            password=test_user_data['password']
        )
        print(f"✓ User created: {user.email}")
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return
    
    # Test 2: Test registration endpoint
    print("\n2. Testing registration endpoint...")
    try:
        # Delete the user we just created to test registration
        user.delete()
        
        response = requests.post(
            f'{base_url}/auth/register/',
            json=test_user_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print("✓ Registration successful")
            print(f"User: {data.get('user', {}).get('email')}")
            print(f"Has tokens: {'tokens' in data}")
        else:
            print(f"✗ Registration failed: {response.text}")
    except Exception as e:
        print(f"✗ Registration error: {e}")
    
    # Test 3: Test login endpoint
    print("\n3. Testing login endpoint...")
    try:
        response = requests.post(
            f'{base_url}/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ Login successful")
            print(f"User: {data.get('user', {}).get('email')}")
            print(f"Has tokens: {'tokens' in data}")
            if 'tokens' in data:
                print(f"Access token length: {len(data['tokens'].get('access', ''))}")
                print(f"Refresh token length: {len(data['tokens'].get('refresh', ''))}")
        else:
            print(f"✗ Login failed: {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
    except Exception as e:
        print(f"✗ Login error: {e}")
    
    # Test 4: Check if server is running
    print("\n4. Testing server connectivity...")
    try:
        response = requests.get(f'{base_url}/auth/register/', timeout=5)
        print(f"Server response: {response.status_code}")
        if response.status_code == 405:  # Method not allowed is expected for GET on POST endpoint
            print("✓ Server is running and responding")
        else:
            print(f"Server status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Is Django running on port 8000?")
    except Exception as e:
        print(f"✗ Server connectivity error: {e}")

if __name__ == '__main__':
    test_backend_auth()
