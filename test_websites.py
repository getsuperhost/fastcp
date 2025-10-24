#!/usr/bin/env python
"""
Website Management API Testing Script for FastCP
"""
import os
import time

import django
from django.contrib.auth import get_user_model
from django.test import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
django.setup()

def test_website_management():
    """Test website management operations"""
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
    login_success = client.login(username='james', password=os.environ.get('TEST_USER_PASSWORD', 'testpass123'))
    if login_success:
        print("✓ Login successful")
    else:
        print("✗ Login failed")
        return

    print("\n--- Testing Website Management ---")

    # Test website listing
    response = client.get('/api/websites/')
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Website listing: {len(data.get('results', []))} websites found")
    else:
        print(f"✗ Website listing failed: {response.status_code}")

    # Test website creation
    timestamp = str(int(time.time()))
    response = client.post('/api/websites/', {
        'label': f'test-website-api-{timestamp}',
        'domains': f'testapi{timestamp}.example.com,www.testapi{timestamp}.example.com',
        'php': '8.3',
        'ssh_user': 'james'
    })
    if response.status_code == 201:
        website_data = response.json()
        website_id = website_data.get('id')
        print(f"✓ Website creation successful: ID {website_id}")
    else:
        print(f"⚠ Website creation: {response.status_code} - {response.json()}")
        return

    # Test domain addition
    if website_id:
        response = client.post(f'/api/websites/{website_id}/add-domain/', {
            'domain': f'newdomain{timestamp}.example.com'
        })
        if response.status_code == 200:
            print("✓ Domain addition successful")
        else:
            print(f"⚠ Domain addition: {response.status_code} - {response.json()}")

    # Test PHP version change
    if website_id:
        response = client.post(f'/api/websites/{website_id}/change-php/', {
            'php': '8.3'
        })
        if response.status_code == 200:
            print("✓ PHP version change successful")
        else:
            print(f"⚠ PHP version change: {response.status_code} - {response.json()}")

    # Test website retrieval
    if website_id:
        response = client.get(f'/api/websites/{website_id}/')
        if response.status_code == 200:
            print("✓ Website retrieval successful")
        else:
            print(f"⚠ Website retrieval: {response.status_code}")

    # Test website deletion
    if website_id:
        response = client.delete(f'/api/websites/{website_id}/')
        if response.status_code == 204:
            print("✓ Website deletion successful")
        else:
            print(f"⚠ Website deletion: {response.status_code} - {response.json()}")

    print("\n--- Website Management Testing Complete ---")

if __name__ == '__main__':
    test_website_management()
