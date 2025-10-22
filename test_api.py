#!/usr/bin/env python
"""
API Testing Script for FastCP
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Set environment variables for testing
os.environ.setdefault('FILE_MANAGER_ROOT', '/tmp/fastcp_users')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
django.setup()

def test_api_endpoints():
    """Test various API endpoints"""
    client = Client()

    # Get the user model
    User = get_user_model()

    # Try to get the test user
    try:
        user = User.objects.get(username='james')
        print(f"✓ Found user: {user.username}")
    except User.DoesNotExist:
        print("✗ User 'james' not found")
        return

    # Login the user
    login_success = client.login(username='james', password='admin123')
    if login_success:
        print("✓ Login successful")
    else:
        print("✗ Login failed")
        return

    # Test API endpoints
    endpoints = [
        ('/api/stats/common/', 'Stats API'),
        ('/api/websites/', 'Websites API'),
        ('/api/ssh-users/', 'Users API'),
        ('/api/databases/', 'Databases API'),
        ('/api/account/', 'Account API'),
        ('/api/file-manager/files/?path=/tmp/fastcp_users/james', 'File Manager API'),
    ]

    for endpoint, name in endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"✓ {name}: {response.status_code} OK")
            else:
                print(f"⚠ {name}: {response.status_code} {response.reason_phrase}")
        except Exception as e:
            print(f"✗ {name}: Error - {str(e)}")

if __name__ == '__main__':
    test_api_endpoints()