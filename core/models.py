import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.template.defaultfilters import slugify

from api.websites.services.get_php_versions import PhpVersionListService


class FastcpUserManager(BaseUserManager):
    """FastCP User Manager.

    This user manager allows us to make customizations to create_superuser
    method to make the auth flow compatible to FastCP's requirements.
    """

    def _create_user(self, **extra_fields):
        """
        Creates a a user for the provided username.
        """
        user = self.model(**extra_fields)
        user.save()
        return user

    def create_superuser(self, username, **kwargs):
        """Create superuser.

        We are overriding this method because the original method requires
        the email address. But we aren't going to have a field for user email.
        """
        return self._create_user(username=username, is_staff=True, is_superuser=True, is_active=True)


class User(AbstractUser):
    """User model.

    We are not relying on password of the user stored in the database nor
    we need their email. Authentication relies on the validation of the unix
    passwords.
    """

    password = models.CharField(max_length=128, blank=True, null=True)
    email = None
    uid = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=30, unique=True)

    # FastCP resource limits
    max_dbs = models.IntegerField(default=10)  # Max number of databases
    max_sites = models.IntegerField(default=10)  # Max number of websites
    storage_used = models.FloatField(default=0)  # Used storage in Bytes
    max_storage = models.FloatField(default=1024)  # Max storage in Bytes

    # More customizations
    REQUIRED_FIELDS = []
    objects = FastcpUserManager()

    def set_password(self, raw_password):
        """Override set_password to do nothing since we use SSH auth."""
        pass

    def check_password(self, raw_password):
        """Override check_password to use our SSH authentication."""
        from .utils.auth import do_login

        return do_login(self.username, raw_password)

    def set_unusable_password(self):
        """Override to do nothing."""
        pass

    def has_usable_password(self):
        """Always return True for our custom authentication."""
        return True

    @property
    def total_dbs(self):
        """Get the count of total databases owned by this user."""
        return self.databases.count()

    @property
    def total_sites(self):
        """Get the count of total sites owned by this user."""
        return self.websites.count()


class Notification(models.Model):
    """Notification model to store important alerts against users."""

    users = models.ManyToManyField(User, related_name="notifications")
    title = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


php_versions = PhpVersionListService().get_php_versions()

PHP_CHOICES = ()
for v in php_versions:
    PHP_CHOICES += ((v, f"PHP {v}"),)


class Website(models.Model):
    """Website model holds the websites owned by users."""

    user = models.ForeignKey(User, related_name="websites", on_delete=models.CASCADE)
    label = models.CharField(max_length=30, unique=True)
    has_ssl = models.BooleanField(default=False)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    php = models.CharField(choices=PHP_CHOICES, max_length=20)
    is_wp = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Always generate a slug on save."""
        if not self.slug:
            i = 0
            while True:
                slug = slugify(self.label)
                if i > 0:
                    slug = f"{slug}-{i}"
                if Website.objects.filter(slug=slug).count() == 0:
                    break
                i += 1
            self.slug = slug
        super(Website, self).save(*args, **kwargs)

    def __str__(self):
        return self.label

    @property
    def metadata(self) -> dict:
        """Returns the meta data for the website"""
        base_path = os.path.join(settings.FILE_MANAGER_ROOT, self.user.username, "apps", self.slug)
        return {
            "path": base_path,
            "pub_path": os.path.join(base_path, "public"),
            "user": self.user.username,
            "ip_addr": settings.SERVER_IP_ADDR,
        }

    def needs_ssl(self) -> bool:
        """Check either website needs SSL or not."""
        return self.domains.filter(ssl=False).count() > 0


class Domain(models.Model):
    """Domain model holds the domains associated to a website."""

    website = models.ForeignKey(Website, related_name="domains", on_delete=models.CASCADE)
    domain = models.CharField(max_length=100, unique=True)
    ssl = models.BooleanField(default=False)
    resolving_ip = models.GenericIPAddressField(null=True, blank=True)
    ssl_error = models.TextField(null=True, blank=True)
    ssl_retries = models.IntegerField(default=0)
    ssl_attempted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.domain


class Database(models.Model):
    """Database model holds the MySQL databases."""

    user = models.ForeignKey(User, related_name="databases", on_delete=models.CASCADE)
    name = models.SlugField(max_length=50, unique=True)
    username = models.SlugField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
