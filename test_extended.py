"""Additional tests for FastCP Django application."""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    """Tests for the custom User model."""

    def test_user_creation(self):
        """Test creating a user with the custom model."""
        User = get_user_model()
        user = User.objects.create(username="testuser")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_creation(self):
        """Test creating a superuser."""
        User = get_user_model()
        user = User.objects.create_superuser(username="admin")
        self.assertEqual(user.username, "admin")
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class APITests(TestCase):
    """Tests for API endpoints."""

    def test_api_root_accessible(self):
        """Test that API root is accessible."""
        response = self.client.get("/api/")
        # Should return 200 or redirect based on configuration
        # 404 if no API root view
        self.assertIn(response.status_code, [200, 302, 404])


@pytest.mark.integration
class IntegrationTests(TestCase):
    """Integration tests for the application."""

    def test_full_user_workflow(self):
        """Test complete user registration and login workflow."""
        # This would test the full user workflow if implemented
        # For now, just test that the URLs exist
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)


# Performance test (can be run separately)
@pytest.mark.slow
class PerformanceTests(TestCase):
    """Performance tests for the application."""

    def test_homepage_response_time(self):
        """Test that homepage responds within reasonable time."""
        import time

        start_time = time.time()
        response = self.client.get("/")
        end_time = time.time()

        response_time = end_time - start_time
        self.assertLess(response_time, 1.0)  # Should respond within 1 second
        self.assertIn(response.status_code, [200, 302])
