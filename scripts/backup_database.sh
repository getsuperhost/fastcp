#!/bin/bash

# FastCP Database Backup Script
# This script creates a backup of the MariaDB database

set -e

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="fastcp_backup_${TIMESTAMP}.sql"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "🔄 Creating database backup..."
echo "📁 Backup location: $BACKUP_DIR/$BACKUP_FILE"

# Create database backup
docker compose exec -T db mariadb-dump \
    -u root \
    -p"password" \
    --single-transaction \
    --routines \
    --triggers \
    --all-databases > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
echo "🗜️ Compressing backup..."
gzip "$BACKUP_DIR/$BACKUP_FILE"

echo "✅ Database backup completed successfully!"
echo "📄 Backup file: $BACKUP_DIR/${BACKUP_FILE}.gz"
echo "📊 File size: $(du -h "$BACKUP_DIR/${BACKUP_FILE}.gz" | cut -f1)"
