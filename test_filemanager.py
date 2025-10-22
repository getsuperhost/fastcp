#!/usr/bin/env python
"""
File Manager API Testing Script for FastCP
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Set environment variables for testing
os.environ.setdefault('FILE_MANAGER_ROOT', '/tmp/fastcp_users')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
django.setup()

def test_file_manager():
    """Test file manager operations"""
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

    # Test file listing
    print("\n--- Testing File Operations ---")
    response = client.get('/api/file-manager/files/?path=/tmp/fastcp_users/james/apps')
    if response.status_code == 200:
        data = response.json()
        print(f"✓ File listing: {len(data.get('files', []))} files found")
        print(f"  Files: {[f['name'] for f in data.get('files', [])]}")
    else:
        print(f"✗ File listing failed: {response.status_code} - {response.json()}")

    # Test file reading
    response = client.get('/api/file-manager/file-manipulation/?path=/tmp/fastcp_users/james/apps/testsite/index.php')
    if response.status_code == 200:
        data = response.json()
        print(f"✓ File read: {len(data.get('content', ''))} characters")
    else:
        print(f"✗ File read failed: {response.status_code} - {response.json()}")

    # Test file upload
    test_file = SimpleUploadedFile("upload_test.txt", b"uploaded content", content_type="text/plain")
    response = client.post('/api/file-manager/upload-files/', {
        'file': test_file,
        'path': '/tmp/fastcp_users/james/apps/testsite'
    })
    if response.status_code == 200:
        print("✓ File upload successful")
    else:
        print(f"⚠ File upload: {response.status_code} - {response.json()}")

    # Test file rename
    response = client.post('/api/file-manager/rename-item/', {
        'path': '/tmp/fastcp_users/james/apps/testsite',
        'old_name': 'index.php',
        'new_name': 'index_renamed.php'
    })
    if response.status_code == 200:
        print("✓ File rename successful")
    else:
        print(f"⚠ File rename: {response.status_code} - {response.json()}")

    # Test directory creation
    response = client.post('/api/file-manager/file-manipulation/', {
        'path': '/tmp/fastcp_users/james/apps',
        'item_name': 'newdir',
        'item_type': 'directory'
    })
    if response.status_code == 200:
        print("✓ Directory creation successful")
    else:
        print(f"⚠ Directory creation: {response.status_code} - {response.json()}")

    print("\n--- File Manager Testing Complete ---")

if __name__ == '__main__':
    test_file_manager()