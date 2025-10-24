# Production Deployment Guide for FastCP

## Overview

This guide provides comprehensive instructions for deploying FastCP, an open-source Ubuntu server control panel, to production environments. FastCP enables hosting multiple PHP/WordPress websites on a single server with features like auto SSL, user isolation, and NGINX reverse proxy.

## Prerequisites

### System Requirements
- **Ubuntu Server**: 20.04 LTS or later (LTS releases only)
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum for OS and applications
- **Network**: Public IP address with DNS configuration

### Software Requirements
- **Docker**: 20.10+ with Docker Compose
- **Git**: For cloning the repository
- **SSL Certificate**: Domain name with DNS configured

## Production Architecture

FastCP uses a containerized architecture with the following components:

```text
┌─────────────────┐    ┌─────────────────┐
│   NGINX Proxy   │    │   FastCP App    │
│   (Port 80/443) │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   MySQL DB      │
                    │   (Port 3306)   │
                    └─────────────────┘
```

## Step 1: Server Preparation



### 1.1 Update System

```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
```



### 1.2 Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Start Docker service
sudo systemctl enable docker
sudo systemctl start docker
```



### 1.3 Configure Firewall

```bash
# Install UFW
sudo apt install ufw -y

# Allow SSH, HTTP, and HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw --force enable
```



### 1.4 Create Deployment Directory

```bash
sudo mkdir -p /opt/fastcp
sudo chown $USER:$USER /opt/fastcp
cd /opt/fastcp
```

## Step 2: SSL Certificate Setup



### 2.1 Install Certbot

```bash
sudo apt install snapd -y
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```



### 2.2 Obtain SSL Certificate

```bash
# Replace yourdomain.com with your actual domain
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```



### 2.3 Set Up Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab for auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Step 3: Application Deployment



### 3.1 Clone Repository

```bash
git clone https://github.com/getsuperhost/fastcp.git .
git checkout master  # or specific production tag
```



### 3.2 Create Production Environment File

```bash
# Create .env file with production settings
cat > .env << EOF
# Django Settings
FASTCP_APP_SECRET=$(openssl rand -hex 32)
IS_DEBUG=0

# Database Settings
FASTCP_SQL_USER=fastcp_prod
FASTCP_SQL_PASSWORD=$(openssl rand -hex 16)
DB_HOST=db

# Domain Settings
FASTCP_DOMAIN=yourdomain.com
FASTCP_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
EOF
```



### 3.3 Create Production Docker Compose Override

```bash
# Create docker-compose.prod.yml
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  db:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD_FILE: /run/secrets/mysql_root_password
      MYSQL_DATABASE: fastcp
      MYSQL_USER_FILE: /run/secrets/mysql_user
      MYSQL_PASSWORD_FILE: /run/secrets/mysql_password
    ports:
      - "127.0.0.1:3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./secrets:/run/secrets:ro
    networks:
      - fastcp_network
    command: --default-authentication-plugin=mysql_native_password

  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    environment:
      - FASTCP_APP_SECRET_FILE=/run/secrets/app_secret
      - FASTCP_SQL_USER_FILE=/run/secrets/mysql_user
      - FASTCP_SQL_PASSWORD_FILE=/run/secrets/mysql_password
      - IS_DEBUG=0
      - DB_HOST=db
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      - db
    volumes:
      - ./secrets:/run/secrets:ro
      - static_files:/app/staticfiles
      - media_files:/app/media
    networks:
      - fastcp_network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
      - ./ssl:/etc/ssl/certs:ro
      - static_files:/var/www/static:ro
      - media_files:/var/www/media:ro
    depends_on:
      - app
    networks:
      - fastcp_network

volumes:
  mysql_data:
  static_files:
  media_files:

networks:
  fastcp_network:
    driver: bridge
EOF
```



### 3.4 Create Secrets Directory

```bash
mkdir -p secrets ssl nginx/sites-enabled

# Create database secrets
echo "fastcp_prod" > secrets/mysql_user
echo "$(openssl rand -hex 16)" > secrets/mysql_password
echo "$(openssl rand -hex 32)" > secrets/mysql_root_password
echo "$(openssl rand -hex 32)" > secrets/app_secret

# Set proper permissions
chmod 600 secrets/*
```



### 3.5 Create Production Dockerfile

```bash
# Create Dockerfile.prod
cat > Dockerfile.prod << EOF
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    build-essential \\
    default-libmysqlclient-dev \\
    pkg-config \\
    nodejs \\
    npm \\
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r app && useradd -r -g app app

# Set work directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package files and install Node.js dependencies
COPY package*.json ./
COPY webpack.mix.js ./
COPY resources/ ./resources/
RUN npm install && npm run production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "fastcp.wsgi:application"]
EOF
```

## Step 4: NGINX Configuration



### 4.1 Create NGINX Configuration
```bash
# Create nginx/nginx.conf
cat > nginx/nginx.conf << EOF
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

    include /etc/nginx/sites-enabled/*.conf;
}
EOF
```



### 4.2 Create Site Configuration
```bash
# Create nginx/sites-enabled/fastcp.conf
cat > nginx/sites-enabled/fastcp.conf << EOF
upstream fastcp_app {
    server app:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/media/;
        expires 30d;
        add_header Cache-Control "public";
    }

    # API endpoints with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://fastcp_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Login endpoint with stricter rate limiting
    location /accounts/login/ {
        limit_req zone=login burst=5 nodelay;
        proxy_pass http://fastcp_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Main application
    location / {
        proxy_pass http://fastcp_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
EOF
```



### 4.3 Copy SSL Certificates
```bash
# Copy SSL certificates to container volume
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
sudo chown $USER:$USER ssl/*
```

## Step 5: Database Setup



### 5.1 Initialize Database
```bash
# Start only the database service
docker-compose -f docker-compose.prod.yml up -d db

# Wait for database to be ready
sleep 30

# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm app python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml run --rm app python manage.py createsuperuser
```

## Step 6: Application Deployment



### 6.1 Build and Start Services
```bash
# Build the application
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps
```



### 6.2 Collect Static Files
```bash
# Collect static files
docker-compose -f docker-compose.prod.yml run --rm app python manage.py collectstatic --noinput
```

## Step 7: Monitoring and Logging



### 7.1 Set Up Log Rotation
```bash
# Create logrotate configuration
sudo cat > /etc/logrotate.d/fastcp << EOF
/var/log/fastcp/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 app app
    postrotate
        docker-compose -f /opt/fastcp/docker-compose.prod.yml restart app
    endscript
}
EOF
```



### 7.2 Install Monitoring Tools
```bash
# Install htop for system monitoring
sudo apt install htop -y

# Install GoAccess for web log analysis
sudo apt install goaccess -y
```



### 7.3 Set Up Health Checks
```bash
# Create health check script
cat > health_check.sh << EOF
#!/bin/bash
# FastCP Health Check Script

echo "=== FastCP Health Check ==="
echo "Timestamp: \$(date)"

# Check Docker services
echo -e "\n--- Docker Services ---"
docker-compose -f docker-compose.prod.yml ps

# Check application health
echo -e "\n--- Application Health ---"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://yourdomain.com/health/

# Check database connectivity
echo -e "\n--- Database Connectivity ---"
docker-compose -f docker-compose.prod.yml exec -T db mysql -u fastcp_prod -p\$FASTCP_SQL_PASSWORD fastcp -e "SELECT 1;" > /dev/null 2>&1
if [ \$? -eq 0 ]; then
    echo "Database: OK"
else
    echo "Database: FAILED"
fi

# Check disk usage
echo -e "\n--- Disk Usage ---"
df -h /opt/fastcp

# Check SSL certificate expiry
echo -e "\n--- SSL Certificate ---"
openssl x509 -in ssl/fullchain.pem -text -noout | grep "Not After" | cut -d: -f2-

echo -e "\n=== Health Check Complete ==="
EOF

chmod +x health_check.sh
```



### 7.4 Set Up Automated Backups
```bash
# Create backup script
cat > backup.sh << EOF
#!/bin/bash
# FastCP Backup Script

BACKUP_DIR="/opt/fastcp/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="fastcp_backup_\${DATE}"

mkdir -p \$BACKUP_DIR

echo "Starting FastCP backup: \$BACKUP_NAME"

# Backup database
docker-compose -f docker-compose.prod.yml exec -T db mysqldump -u fastcp_prod -p\$FASTCP_SQL_PASSWORD fastcp > \$BACKUP_DIR/\${BACKUP_NAME}_db.sql

# Backup application data
tar -czf \$BACKUP_DIR/\${BACKUP_NAME}_app.tar.gz -C /opt/fastcp . --exclude='backups' --exclude='logs/*.log'

# Backup SSL certificates
tar -czf \$BACKUP_DIR/\${BACKUP_NAME}_ssl.tar.gz -C /etc/letsencrypt live/yourdomain.com

# Clean old backups (keep last 7 days)
find \$BACKUP_DIR -name "*.tar.gz" -o -name "*.sql" -mtime +7 -delete

echo "Backup completed: \$BACKUP_NAME"
EOF

chmod +x backup.sh

# Add to crontab for daily backups at 2 AM
echo "0 2 * * * /opt/fastcp/backup.sh" | crontab -
```

## Step 8: Security Hardening



### 8.1 Update Docker Compose Security
```bash
# Update docker-compose.prod.yml with security improvements
cat >> docker-compose.prod.yml << EOF

# Add security constraints
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    volumes:
      - ./logs:/app/logs
EOF
```



### 8.2 Configure Fail2Ban
```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Create FastCP jail
sudo cat > /etc/fail2ban/jail.d/fastcp.conf << EOF
[fastcp]
enabled = true
port = http,https
filter = fastcp
logpath = /var/log/nginx/access.log
maxretry = 3
bantime = 3600
EOF

# Create filter
sudo cat > /etc/fail2ban/filter.d/fastcp.conf << EOF
[Definition]
failregex = ^<HOST> -.*"(GET|POST|PUT|DELETE).*" (401|403|404) .*$
ignoreregex =
EOF

# Restart Fail2Ban
sudo systemctl restart fail2ban
```

## Step 9: Performance Optimization



### 9.1 Database Optimization
```bash
# Create MySQL optimization configuration
cat > mysql-optimization.cnf << EOF
[mysqld]
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
query_cache_size = 64M
max_connections = 100
EOF

# Update docker-compose.prod.yml to include optimization
sed -i '/command:/a\      --defaults-extra-file=/etc/mysql/mysql.conf.d/mysql-optimization.cnf' docker-compose.prod.yml
```



### 9.2 Gunicorn Optimization
```bash
# Update Dockerfile.prod CMD for better performance
sed -i 's/CMD \["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "fastcp.wsgi:application"\]/CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--max-requests", "1000", "--max-requests-jitter", "50", "fastcp.wsgi:application"]/' Dockerfile.prod
```

## Step 10: Maintenance and Updates



### 10.1 Update Procedure
```bash
# Create update script
cat > update.sh << EOF
#!/bin/bash
# FastCP Update Script

echo "Starting FastCP update..."

# Backup current version
./backup.sh

# Pull latest changes
git pull origin master

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Run migrations if needed
docker-compose -f docker-compose.prod.yml run --rm app python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml run --rm app python manage.py collectstatic --noinput

echo "FastCP update completed!"
EOF

chmod +x update.sh
```



### 10.2 Monitoring Commands
```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Monitor resource usage
docker stats

# Check application logs
docker-compose -f docker-compose.prod.yml logs app

# Run health check
./health_check.sh
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database service
   docker-compose -f docker-compose.prod.yml logs db

   # Verify database credentials
   docker-compose -f docker-compose.prod.yml exec db mysql -u fastcp_prod -p
   ```

2. **SSL Certificate Issues**
   ```bash
   # Renew certificates
   sudo certbot renew

   # Copy updated certificates
   sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
   sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
   sudo chown $USER:$USER ssl/*

   # Restart NGINX
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

3. **Application Not Starting**
   ```bash
   # Check application logs
   docker-compose -f docker-compose.prod.yml logs app

   # Run application manually for debugging
   docker-compose -f docker-compose.prod.yml run --rm app python manage.py check
   ```

## Security Checklist

- [ ] SSL certificates properly configured and auto-renewing
- [ ] Database credentials stored securely in secrets
- [ ] Firewall configured (UFW)
- [ ] Docker containers running as non-root users
- [ ] Fail2Ban configured for brute force protection
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] Security headers enabled in NGINX
- [ ] Rate limiting configured for API endpoints
- [ ] Regular security updates scheduled

## Performance Monitoring

Monitor these key metrics:
- **Response Time**: < 500ms for API endpoints
- **CPU Usage**: < 70% average
- **Memory Usage**: < 80% of available RAM
- **Database Connections**: Monitor connection pool usage
- **SSL Certificate Expiry**: > 30 days remaining

## Support

For issues and questions:
- Check the [FastCP GitHub Repository](https://github.com/getsuperhost/fastcp)
- Review Docker and NGINX logs
- Run the health check script for diagnostics

---

**Note**: This deployment guide assumes a single-server setup. For high-availability deployments with multiple servers, additional configuration for load balancing and database clustering would be required.</content>
<parameter name="filePath">/mnt/c/Users/james/OneDrive/Desktop/fastcp/PRODUCTION_DEPLOYMENT.md