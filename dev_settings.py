# FastCP Development Configuration
# This file contains development-specific settings and overrides

# Development Server Configuration
DEBUG = True
IS_DEBUG = True

# Database Configuration (SQLite for development)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

# Email Configuration (Console backend for development)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/debug.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "fastcp": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}

# Django Debug Toolbar (if installed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8899",
    "http://127.0.0.1:8899",
]

# File upload settings for development
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB

# Session settings
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_DOMAIN = None

# Security settings (relaxed for development)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Static files configuration
STATIC_URL = "/static/"
STATIC_ROOT = "staticfiles"
STATICFILES_DIRS = [
    "static",
]

# Media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = "media"

# Cache configuration (no caching for development)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Development-specific settings
DEVELOPMENT_PORT = 8899
VERSION = "1.0.0-dev"

# REST Framework settings for development
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {},
}
