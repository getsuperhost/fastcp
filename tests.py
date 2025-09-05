"""Tests for FastCP Django application."""

import pytest
from django.test import TestCase


class BasicTests(TestCase):
    """Basic functionality tests."""

    def test_homepage_accessible(self):
        """Test that the homepage is accessible."""
        response = self.client.get("/")
        # Should redirect to admin or return a valid response
        self.assertIn(response.status_code, [200, 302])

    @pytest.mark.unit
    def test_admin_login_page(self):
        """Test that admin login page is accessible."""
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django administration")
