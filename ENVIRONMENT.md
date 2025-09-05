# FastCP Environment Variables Configuration

This document describes all environment variables used by FastCP and their default values.

## Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | None | Full database URL (e.g., `mysql://user:pass@host:port/db`) |
| `DB_NAME` | `fastcp` | Database name (used when DATABASE_URL not set) |
| `DB_USER` | `postgres` | Database username (legacy, now uses root for MySQL) |
| `DB_PASSWORD` | `password` | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port (legacy PostgreSQL, now 3306 for MySQL) |

## Application Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `IS_DEBUG` | None | Enable debug mode (any value enables it) |
| `FASTCP_APP_SECRET` | `django-insecure-...` | Django secret key |
| `LOG_LEVEL` | `DEBUG` | Logging level |
| `PORT` | `8899` | Application port |
| `ALLOWED_HOSTS` | `*` | Comma-separated list of allowed hosts |

## FastCP Specific Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `FASTCP_VERSION` | `1.1.0` | FastCP version |
| `FASTCP_SITE_NAME` | `FastCP` | Site name |
| `FASTCP_SITE_URL` | `https://fastcp.org` | Site URL |
| `FASTCP_SQL_PASSWORD` | None | SQL admin password |
| `FASTCP_SQL_USER` | None | SQL admin user |
| `FASTCP_PHPMYADMIN_PATH` | `/var/fastcp/phpmyadmin` | phpMyAdmin installation path |

## File System Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FILE_MANAGER_ROOT` | `/srv/users` | Root directory for file manager |
| `PHP_INSTALL_PATH` | `/etc/php` | PHP installation path |
| `NGINX_BASE_DIR` | `/etc/nginx` | Nginx configuration directory |
| `NGINX_VHOSTS_ROOT` | `/etc/nginx/vhosts.d` | Nginx virtual hosts directory |
| `APACHE_VHOST_ROOT` | `/etc/apache2/vhosts.d` | Apache virtual hosts directory |

## SSL/TLS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LETSENCRYPT_IS_STAGING` | None | Use Let's Encrypt staging environment |
| `SECURE_SSL_REDIRECT` | `0` | Force SSL redirect |
| `SESSION_COOKIE_SECURE` | `0` | Secure session cookies |
| `CSRF_COOKIE_SECURE` | `0` | Secure CSRF cookies |

## Server Information

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_IP_ADDR` | `N/A` | Server IP address |
| `HOSTNAME` | System hostname | Container hostname |

## Docker Compose Environment

The following environment variables are set in `docker-compose.override.yml`:

```yaml
environment:
  - IS_DEBUG=1
  - DJANGO_SETTINGS_MODULE=fastcp.settings
  - SECRET_KEY=django-insecure-dev-key-change-in-production
  - LOG_LEVEL=DEBUG
  - DATABASE_URL=mysql://root:password@db:3306/fastcp
```

## Development vs Production

### Development (docker-compose.override.yml)
- `IS_DEBUG=1` - Enables Django debug mode
- `SECRET_KEY` - Uses insecure development key
- `DATABASE_URL` - Points to local MariaDB container
- Hot reload enabled with volume mounting

### Production Recommendations
- Set `IS_DEBUG` to empty or remove entirely
- Use a strong, unique `FASTCP_APP_SECRET`
- Configure proper `DATABASE_URL` for production database
- Set appropriate `ALLOWED_HOSTS`
- Enable SSL with `SECURE_SSL_REDIRECT=1`
- Use secure cookies in production

## Examples

### Local Development
```bash
export IS_DEBUG=1
export DATABASE_URL="mysql://root:password@localhost:3306/fastcp"
```

### Production
```bash
export FASTCP_APP_SECRET="your-very-secret-key-here"
export DATABASE_URL="mysql://fastcp_user:secure_password@prod-db:3306/fastcp_prod"
export ALLOWED_HOSTS="fastcp.yourcompany.com,www.yourcompany.com"
export SECURE_SSL_REDIRECT=1
```
