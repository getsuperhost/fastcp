"""
Django settings for fastcp project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('FASTCP_APP_SECRET', 'django-insecure-swm^3n$0#i^x3uuh3hy&_h(%ud$a6qfo6#tnukvxmyem7j3x8=')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# As the IP of the server may change, we cannot reliably whitelist any hosts. So
# allowing all hosts is fine and secure as we are not going to rely on the host
# header for any purpose.
ALLOWED_HOSTS = ['*']


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.FastcpPagination',
    'PAGE_SIZE': 10,
    'DATETIME_FORMAT': '%b %d, %Y %H:%M:%S',
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'django_cron',
    'api',
    'core'
]

CRON_CLASSES = [
    'core.crons.ProcessSsls'
]
DJANGO_CRON_DELETE_LOGS_OLDER_THAN = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.BlockUnwantedExtensionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS += [
        'whitenoise.runserver_nostatic',
    ]
else:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Disable suffix URLs (like .php) in admin
APPEND_SLASH = True
ADMIN_FORCE_HTTPS = True  # Force HTTPS for admin pages

ROOT_URLCONF = 'fastcp.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context.general_settings'
            ],
        },
    },
]

WSGI_APPLICATION = 'fastcp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'fastcp'),
        'USER': os.environ.get('MYSQL_USER', 'fastcpuser'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'fastcppass'),
        'HOST': os.environ.get('MYSQL_HOST', 'mariadb'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'ssl': {'ca': None}
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'core.User'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'core.storage.WhiteNoiseStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# FastCP's added settings
FASTCP_SITE_NAME = 'FastCP'
FASTCP_SITE_URL = 'https://fastcp.org'
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'spa'
FILE_MANAGER_ROOT = os.environ.get('FILE_MANAGER_ROOT', '/srv/users')
PHP_INSTALL_PATH = os.environ.get('PHP_INSTALL_PATH', '/etc/php')
NGINX_BASE_DIR = os.environ.get('NGINX_BASE_DIR', '/etc/nginx')
NGINX_VHOSTS_ROOT = os.environ.get('NGINX_VHOSTS_ROOT', '/etc/nginx/vhosts.d')
APACHE_VHOST_ROOT = os.environ.get('APACHE_VHOST_ROOT', '/etc/apache2/vhosts.d')
FASTCP_VERSION = os.environ.get('FASTCP_VERSION', '1.0.1')
LETSENCRYPT_IS_STAGING = os.environ.get('LETSENCRYPT_IS_STAGING') is not None
SERVER_IP_ADDR = os.environ.get('SERVER_IP_ADDR', 'N/A')
FASTCP_SQL_PASSWORD = os.environ.get('FASTCP_SQL_PASSWORD')
FASTCP_SQL_USER = os.environ.get('FASTCP_SQL_USER')
FASTCP_PHPMYADMIN_PATH = os.environ.get('FASTCP_PHPMYADMIN_PATH', '/var/fastcp/phpmyadmin')