# Production Monitoring and Logging Setup for FastCP

## Overview

This guide provides comprehensive monitoring and logging setup for FastCP production deployments. It includes application logging, system monitoring, health checks, and alerting configurations.

## Application Logging Configuration

### 1.1 Django Logging Setup

Update `fastcp/settings.py` for production logging:

```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/fastcp.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/fastcp_error.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 1.2 Gunicorn Logging

Update the production Dockerfile to include proper Gunicorn logging:

```dockerfile
# In Dockerfile.prod, update the CMD
CMD ["gunicorn", "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--log-level", "info", \
     "--access-logfile", "/app/logs/gunicorn_access.log", \
     "--error-logfile", "/app/logs/gunicorn_error.log", \
     "--capture-output", \
     "fastcp.wsgi:application"]
```

### 1.3 NGINX Access Logging

Update NGINX configuration for detailed access logging:

```nginx
# In nginx/nginx.conf, update the log_format
log_format detailed '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time $upstream_response_time $pipe';

access_log /var/log/nginx/fastcp_access.log detailed;
error_log /var/log/nginx/fastcp_error.log;
```

## System Monitoring Setup

### 2.1 Prometheus Monitoring

Create Prometheus configuration for FastCP metrics:

```yaml
# Create prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'fastcp'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:8080']
    scrape_interval: 5s

  - job_name: 'mysql'
    static_configs:
      - targets: ['db:3306']
    scrape_interval: 15s
```

### 2.2 Grafana Dashboards

Create Grafana dashboard configuration for FastCP monitoring:

```json
{
  "dashboard": {
    "title": "FastCP Production Monitoring",
    "tags": ["fastcp", "production"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Application Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])",
            "legendFormat": "Response Time"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "mysql_global_status_threads_connected",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "title": "System CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ]
      },
      {
        "title": "System Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)",
            "legendFormat": "Memory Usage %"
          }
        ]
      }
    ]
  }
}
```

### 2.3 Docker Compose Monitoring Stack

Add monitoring services to docker-compose.prod.yml:

```yaml
# Add to docker-compose.prod.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - fastcp_network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - prometheus
    networks:
      - fastcp_network

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - fastcp_network

volumes:
  prometheus_data:
  grafana_data:
```

## Health Checks and Alerting

### 3.1 Application Health Endpoints

Create Django health check endpoints:

```python
# In core/views.py, add health check views
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import psutil
import os

def health_check(request):
    """Basic health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'fastcp'
    })

def detailed_health_check(request):
    """Detailed health check with system metrics"""
    try:
        # Database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return JsonResponse({
        'status': 'healthy' if db_status == 'healthy' and cpu_percent < 90 else 'degraded',
        'timestamp': timezone.now().isoformat(),
        'checks': {
            'database': db_status,
            'cpu_usage': f"{cpu_percent}%",
            'memory_usage': f"{memory.percent}%",
            'disk_usage': f"{disk.percent}%"
        }
    })

# In core/urls.py, add URL patterns
urlpatterns = [
    # ... existing patterns ...
    path('health/', health_check, name='health_check'),
    path('health/detailed/', detailed_health_check, name='detailed_health_check'),
]
```

### 3.2 Prometheus Metrics Endpoint

Add Django Prometheus metrics:

```python
# Install django-prometheus
# Add to requirements.txt
django-prometheus==2.3.1

# In settings.py, add middleware
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... other middleware ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# In urls.py, add metrics endpoint
from django_prometheus import exports
urlpatterns = [
    # ... existing patterns ...
    path('metrics/', exports.ExportToDjangoView, name='metrics'),
]
```

### 3.3 Alert Manager Configuration

Create AlertManager configuration for notifications:

```yaml
# Create alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'email'
  routes:
  - match:
      alertname: 'FastCPDown'
    receiver: 'email'
    group_wait: 10s

receivers:
- name: 'email'
  email_configs:
  - to: 'admin@yourdomain.com'
    send_resolved: true

# Alert rules
groups:
- name: fastcp
  rules:
  - alert: FastCPDown
    expr: up{job="fastcp"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "FastCP application is down"
      description: "FastCP has been down for more than 5 minutes."

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 85% for more than 5 minutes."

  - alert: HighMemoryUsage
    expr: 100 - ((node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100) > 90
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is above 90% for more than 5 minutes."
```

## Log Aggregation and Analysis

### 4.1 ELK Stack Setup

Add ELK stack to docker-compose for log aggregation:

```yaml
# Add to docker-compose.prod.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - fastcp_network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    ports:
      - "5044:5044"
    volumes:
      - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf:ro
    depends_on:
      - elasticsearch
    networks:
      - fastcp_network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - fastcp_network

volumes:
  elasticsearch_data:
```

### 4.2 Logstash Configuration

Create Logstash configuration for FastCP logs:

```conf
# Create monitoring/logstash.conf
input {
  file {
    path => "/app/logs/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }

  file {
    path => "/var/log/nginx/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}

filter {
  if [path] =~ /fastcp\.log$/ {
    grok {
      match => { "message" => "%{LOGLEVEL:level} %{TIMESTAMP_ISO8601:timestamp} %{WORD:module} %{NUMBER:process} %{NUMBER:thread} %{GREEDYDATA:message}" }
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }

  if [path] =~ /nginx/ {
    grok {
      match => { "message" => "%{IP:client} - %{USERNAME:remote_user} \[%{HTTPDATE:timestamp}\] \"%{WORD:method} %{URIPATHPARAM:request} HTTP/%{NUMBER:httpversion}\" %{NUMBER:status} %{NUMBER:bytes} \"%{URI:referer}\" \"%{DATA:user_agent}\" %{NUMBER:request_time} %{NUMBER:upstream_time} %{DATA:pipe}" }
    }
    date {
      match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "fastcp-%{+YYYY.MM.dd}"
  }
  stdout { codec => rubydebug }
}
```

## Automated Monitoring Scripts

### 5.1 System Monitoring Script

Create comprehensive system monitoring script:

```bash
#!/bin/bash
# FastCP System Monitoring Script

MONITOR_LOG="/opt/fastcp/logs/monitor.log"
THRESHOLD_CPU=80
THRESHOLD_MEMORY=85
THRESHOLD_DISK=90

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $MONITOR_LOG
}

# CPU Monitoring
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
if (( $(echo "$CPU_USAGE > $THRESHOLD_CPU" | bc -l) )); then
    log_message "WARNING: High CPU usage detected: ${CPU_USAGE}%"
fi

# Memory Monitoring
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if (( MEMORY_USAGE > THRESHOLD_MEMORY )); then
    log_message "WARNING: High memory usage detected: ${MEMORY_USAGE}%"
fi

# Disk Monitoring
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if (( DISK_USAGE > THRESHOLD_DISK )); then
    log_message "WARNING: High disk usage detected: ${DISK_USAGE}%"
fi

# Service Health Checks
if ! docker-compose -f /opt/fastcp/docker-compose.prod.yml ps | grep -q "Up"; then
    log_message "CRITICAL: Some FastCP services are not running"
fi

# SSL Certificate Check
SSL_EXPIRY=$(openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout | grep "Not After" | cut -d: -f2-)
SSL_DAYS_LEFT=$(( ($(date -d "$SSL_EXPIRY" +%s) - $(date +%s)) / 86400 ))
if (( SSL_DAYS_LEFT < 30 )); then
    log_message "WARNING: SSL certificate expires in ${SSL_DAYS_LEFT} days"
fi

log_message "Monitoring check completed"
```

### 5.2 Log Rotation Setup

Configure log rotation for all FastCP logs:

```bash
# Create /etc/logrotate.d/fastcp-monitoring
/opt/fastcp/logs/*.log /var/log/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/fastcp/docker-compose.prod.yml restart logstash 2>/dev/null || true
    endscript
}
```

### 5.3 Automated Backup Monitoring

Enhance backup script with monitoring:

```bash
#!/bin/bash
# Enhanced FastCP Backup Script with Monitoring

BACKUP_DIR="/opt/fastcp/backups"
LOG_FILE="/opt/fastcp/logs/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="fastcp_backup_${DATE}"

log_backup() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - BACKUP: $1" >> $LOG_FILE
}

log_backup "Starting backup: $BACKUP_NAME"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup with error checking
if docker-compose -f /opt/fastcp/docker-compose.prod.yml exec -T db mysqldump -u fastcp_prod -p$FASTCP_SQL_PASSWORD fastcp > $BACKUP_DIR/${BACKUP_NAME}_db.sql 2>>$LOG_FILE; then
    log_backup "Database backup successful"
else
    log_backup "ERROR: Database backup failed"
    exit 1
fi

# Application data backup
if tar -czf $BACKUP_DIR/${BACKUP_NAME}_app.tar.gz -C /opt/fastcp . --exclude='backups' --exclude='logs/*.log' 2>>$LOG_FILE; then
    log_backup "Application backup successful"
else
    log_backup "ERROR: Application backup failed"
    exit 1
fi

# SSL certificates backup
if tar -czf $BACKUP_DIR/${BACKUP_NAME}_ssl.tar.gz -C /etc/letsencrypt live/yourdomain.com 2>>$LOG_FILE; then
    log_backup "SSL backup successful"
else
    log_backup "ERROR: SSL backup failed"
    exit 1
fi

# Verify backup integrity
if gzip -t $BACKUP_DIR/${BACKUP_NAME}_db.sql.gz 2>/dev/null && tar -tzf $BACKUP_DIR/${BACKUP_NAME}_app.tar.gz >/dev/null 2>&1; then
    log_backup "Backup integrity check passed"
else
    log_backup "ERROR: Backup integrity check failed"
    exit 1
fi

# Clean old backups
find $BACKUP_DIR -name "*.tar.gz" -o -name "*.sql" -mtime +7 -delete

# Send notification (if configured)
if command -v mail >/dev/null 2>&1; then
    echo "FastCP backup completed successfully: $BACKUP_NAME" | mail -s "FastCP Backup Success" admin@yourdomain.com
fi

log_backup "Backup completed successfully: $BACKUP_NAME"
```

## Deployment Instructions

### 6.1 Deploy Monitoring Stack

```bash
# Create monitoring directories
mkdir -p monitoring/prometheus monitoring/grafana/provisioning/datasources monitoring/logstash logs

# Deploy monitoring services
docker-compose -f docker-compose.prod.yml up -d prometheus grafana node-exporter

# Wait for services to start
sleep 30

# Import Grafana dashboard
curl -X POST -H "Content-Type: application/json" -d @monitoring/grafana/dashboard.json http://admin:admin_password@localhost:3000/api/dashboards/db
```

### 6.2 Set Up Cron Jobs

```bash
# Add monitoring cron jobs
(crontab -l ; echo "*/5 * * * * /opt/fastcp/monitoring/monitor.sh") | crontab -
(crontab -l ; echo "0 2 * * * /opt/fastcp/backup.sh") | crontab -

# Set up log rotation
sudo cp monitoring/logrotate/fastcp /etc/logrotate.d/
sudo systemctl restart logrotate
```

### 6.3 Configure Alerts

```bash
# Start AlertManager
docker run -d --name alertmanager -p 9093:9093 \
  -v /opt/fastcp/monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager

# Configure Prometheus to use AlertManager
# Add to prometheus.yml
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093
```

## Monitoring Dashboard Access

- **Grafana**: `http://yourdomain.com:3000` (admin/admin_password)
- **Prometheus**: `http://yourdomain.com:9090`
- **AlertManager**: `http://yourdomain.com:9093`
- **Kibana**: `http://yourdomain.com:5601`

## Key Metrics to Monitor

1. **Application Performance**
   - Response time percentiles (p50, p95, p99)
   - Error rates by endpoint
   - Throughput (requests per second)

2. **System Resources**
   - CPU usage trends
   - Memory consumption
   - Disk I/O and space
   - Network traffic

3. **Database Performance**
   - Connection pool usage
   - Query execution times
   - Lock wait times
   - Buffer pool hit ratio

4. **Security Metrics**
   - Failed login attempts
   - SSL certificate expiry
   - Unusual traffic patterns

## Troubleshooting Monitoring

### Common Issues

1. **Prometheus not scraping metrics**

   ```bash
   # Check Prometheus targets
   curl http://localhost:9090/api/v1/targets

   # Verify application metrics endpoint
   curl http://localhost:8000/metrics
   ```

2. **Grafana not displaying data**

   ```bash
   # Check Grafana logs
   docker-compose logs grafana

   # Verify Prometheus data source
   curl http://localhost:3000/api/datasources
   ```

3. **Logstash not processing logs**

   ```bash
   # Check Logstash logs
   docker-compose logs logstash

   # Verify log file permissions
   ls -la /opt/fastcp/logs/
   ```

## Maintenance Tasks

### Weekly

- Review monitoring dashboards
- Check log aggregation for errors
- Verify backup integrity

### Monthly

- Update monitoring stack versions
- Review and optimize alert rules
- Analyze performance trends

### Quarterly

- Security audit of monitoring infrastructure
- Capacity planning based on metrics
- Update monitoring documentation

---

This monitoring setup provides comprehensive observability for FastCP production deployments, ensuring high availability and quick issue resolution.
