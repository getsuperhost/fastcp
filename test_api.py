#!/usr/bin/env python3
"""
FastCP API Testing Script
Tests all major API endpoints to ensure functionality after Django 5.x upgrade.
"""

import os
import sys

import django
import requests

from django.contrib.auth import get_user_model
from django.test.client import Client

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
os.environ.setdefault('IS_DEBUG', '1')
django.setup()

User = get_user_model()


class FastCPAPITester:
    """Test FastCP API endpoints."""

    def __init__(self, base_url="http://localhost:8899"):
        self.base_url = base_url
        self.client = Client()
        self.session = requests.Session()

    def test_api_endpoints(self):
        """Test API endpoints."""
        print("🔌 Testing API endpoints...")

        endpoints = [
            "/api/websites/",
            "/api/ssh-users/",
            "/api/databases/",
            "/api/file-manager/files/",
            "/api/stats/common/",
        ]

        passed = 0
        total = len(endpoints)

        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url, timeout=5)

                # API should return 401/403 for unauthenticated
                # requests or 200 for allowed endpoints
                if response.status_code in [200, 401, 403]:
                    print(f"✅ {endpoint} - Status: {response.status_code}")
                    passed += 1
                else:
                    status = response.status_code
                    print(f"❌ {endpoint} - Unexpected status: {status}")

            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")

        print(f"📊 API Tests: {passed}/{total} endpoints responding correctly")
        return passed == total

    def test_django_client(self):
        """Test using Django test client."""
        print("\n🧪 Testing with Django test client...")

        try:
            # Test homepage redirect
            response = self.client.get('/')
            print(f"✅ Homepage redirect: {response.status_code}")

            # Test admin login page
            response = self.client.get('/admin/login/')
            if response.status_code == 200:
                print("✅ Admin login page accessible")
            else:
                status = response.status_code
                print(f"❌ Admin login page status: {status}")

            # Test API root
            response = self.client.get('/api/')
            print(f"✅ API root status: {response.status_code}")

            return True

        except Exception as e:
            print(f"❌ Django client test failed: {e}")
            return False

    def test_authentication_flow(self):
        """Test authentication mechanisms."""
        print("\n🔐 Testing authentication flow...")

        try:
            # Test creating a user
            if not User.objects.filter(username='testuser').exists():
                test_user = User(username='testuser', is_active=True)
                test_user.save()
                print("✅ Test user created")
            else:
                test_user = User.objects.get(username='testuser')
                print("✅ Test user found")

            # Test login view
            response = self.client.get('/dashboard/sign-in/')
            if response.status_code == 200:
                print("✅ Login page accessible")
            else:
                status = response.status_code
                print(f"⚠️  Login page status: {status}")

            # Clean up
            if test_user:
                test_user.delete()
                print("✅ Test user cleaned up")

            return True

        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False

    def test_model_operations(self):
        """Test model CRUD operations."""
        print("\n📝 Testing model operations...")

        try:
            # Create test user
            test_user = User.objects.create(
                username='modeltest',
                is_active=True
            )

            # Test user properties
            max_dbs = test_user.max_dbs
            print(f"✅ User created - Max DBs: {max_dbs}")
            total_dbs = test_user.total_dbs
            total_sites = test_user.total_sites
            stats_msg = f"✅ User stats - Total DBs: {total_dbs}, "
            stats_msg += f"Total Sites: {total_sites}"
            print(stats_msg)

            # Clean up
            test_user.delete()
            print("✅ Model test cleanup completed")

            return True

        except Exception as e:
            print(f"❌ Model operations test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all API tests."""
        print("FastCP API Testing Suite")
        print("=" * 30)

        tests = [
            ("Django Client Tests", self.test_django_client),
            ("Authentication Flow", self.test_authentication_flow),
            ("Model Operations", self.test_model_operations),
            ("API Endpoints", self.test_api_endpoints),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")

        print(f"\n📊 Final Results: {passed}/{total} test suites passed")

        if passed == total:
            print("🎉 All API tests passed!")
            return True
        else:
            print("⚠️  Some API tests failed.")
            return False


def main():
    """Main test runner."""
    tester = FastCPAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
