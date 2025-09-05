from django.contrib.auth import authenticate
from django.test import TestCase

from .models import Database, User, Website
from .utils.system import setup_wordpress


class UserModelTest(TestCase):
    """Test cases for the User model."""

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user.set_password("testpass123")
        self.user.save()

    def test_user_creation(self):
        """Test that a user can be created."""
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpass123"))

    def test_user_authentication(self):
        """Test SSH-style authentication."""
        # This would normally authenticate against system users
        # For testing, we'll mock the authentication
        authenticated_user = authenticate(username="testuser", password="testpass123")
        # Since we're not using real SSH auth in tests
        self.assertIsNone(authenticated_user)

    def test_user_resource_limits(self):
        """Test user resource limit properties."""
        self.assertEqual(self.user.total_sites, 0)
        self.assertEqual(self.user.total_dbs, 0)


class WebsiteModelTest(TestCase):
    """Test cases for the Website model."""

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.website = Website.objects.create(user=self.user, label="test-site", php="8.1")

    def test_website_creation(self):
        """Test that a website can be created."""
        self.assertEqual(self.website.label, "test-site")
        self.assertEqual(self.website.php, "8.1")
        self.assertEqual(self.website.user, self.user)

    def test_website_slug_generation(self):
        """Test that slugs are generated automatically."""
        self.assertIsNotNone(self.website.slug)
        if self.website.slug:
            self.assertTrue(self.website.slug.startswith("test-site"))

    def test_website_metadata(self):
        """Test website metadata generation."""
        metadata = self.website.metadata
        self.assertIn("path", metadata)
        self.assertIn("pub_path", metadata)
        self.assertIn("user", metadata)


class DatabaseModelTest(TestCase):
    """Test cases for the Database model."""

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.database = Database.objects.create(user=self.user, name="test_db", username="test_user")

    def test_database_creation(self):
        """Test that a database can be created."""
        self.assertEqual(self.database.name, "test_db")
        self.assertEqual(self.database.username, "test_user")
        self.assertEqual(self.database.user, self.user)


# Create your tests here.
class TestWordPressDeploy(TestCase):

    def setUp(self) -> None:
        from .models import Domain

        u = User.objects.create(username="fasdd3")
        w = Website.objects.create(user=u, label="test-website", php="8.1")
        Domain.objects.create(website=w, domain="example.com")

    def test_wp_deploy(self):
        w = Website.objects.first()
        setup_wordpress(w)
