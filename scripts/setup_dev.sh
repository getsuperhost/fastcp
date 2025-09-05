#!/bin/bash

# FastCP Development Environment Setup Script
# This script sets up the development environment from scratch

set -e

echo "🚀 Setting up FastCP Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down || true

# Build and start services
echo "🏗️ Building and starting services..."
docker compose up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 15

# Check if database is healthy
until docker compose exec db mariadb -u root -p"password" -e "SELECT 1" fastcp > /dev/null 2>&1; do
    echo "⏳ Waiting for MariaDB to be ready..."
    sleep 5
done

echo "✅ Database is ready!"

# Run migrations
echo "🔄 Running database migrations..."
docker compose exec fastcp python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
docker compose exec fastcp python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('✅ Superuser created: admin/admin')
else:
    print('ℹ️ Superuser already exists')
" 2>/dev/null || echo "⚠️ Superuser creation skipped"

# Collect static files
echo "📦 Collecting static files..."
docker compose exec fastcp python manage.py collectstatic --noinput

# Show status
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🎉 Development environment setup complete!"
echo "🌐 Application URL: http://localhost:8899"
echo "🔧 Admin URL: http://localhost:8899/admin"
echo "📊 Database: MariaDB 11.8 on localhost:3306"
echo ""
echo "To stop the environment: docker compose down"
echo "To view logs: docker compose logs -f"
