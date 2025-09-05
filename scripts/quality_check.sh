#!/bin/bash

# FastCP Code Quality Check Script
# This script runs various code quality checks

set -e

echo "🔍 Running FastCP Code Quality Checks..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python code style
echo "📏 Checking Python code style with autopep8..."
if docker compose exec fastcp python -c "import autopep8" 2>/dev/null; then
    docker compose exec fastcp find . -name "*.py" -not -path "./staticfiles/*" -not -path "./.git/*" -exec autopep8 --diff {} \; || true
else
    echo "⚠️ autopep8 not available in container"
fi

# Run Django system checks
echo "🔧 Running Django system checks..."
docker compose exec fastcp python manage.py check

# Check for migrations
echo "📊 Checking for pending migrations..."
docker compose exec fastcp python manage.py showmigrations | grep "\[ \]" && echo "⚠️ Unapplied migrations found!" || echo "✅ All migrations applied"

# Test database connectivity
echo "🔗 Testing database connectivity..."
docker compose exec fastcp python manage.py dbshell --command "SELECT VERSION();" || echo "⚠️ Database connectivity issue"

# Check for security issues
echo "🛡️ Running Django security checks..."
docker compose exec fastcp python manage.py check --deploy --settings=fastcp.settings || echo "⚠️ Security issues found"

# Show current service status
echo "📊 Current service status:"
docker compose ps

echo ""
echo "✅ Code quality checks completed!"
echo "💡 Consider running: ./scripts/backup_database.sh before making changes"
