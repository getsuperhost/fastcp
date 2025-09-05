#!/usr/bin/env python3
"""
FastCP Upgrade Validation Script
Validates that the Django 5.x upgrade is working correctly.
"""

import os
import sys
import django
import requests
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
os.environ.setdefault('IS_DEBUG', '1')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.auth import get_user_model
from core.models import Website, Database, Domain

User = get_user_model()

def check_database_connection():
    """Test database connectivity."""
    print("🔗 Testing database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
            print(f"   Database engine: {connection.vendor}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_models():
    """Test model functionality."""
    print("\n📊 Testing models...")
    try:
        # Test User model
        user_count = User.objects.count()
        print(f"✅ User model working - {user_count} users")
        
        # Test Website model  
        website_count = Website.objects.count()
        print(f"✅ Website model working - {website_count} websites")
        
        # Test Database model
        db_count = Database.objects.count()
        print(f"✅ Database model working - {db_count} databases")
        
        # Test Domain model
        domain_count = Domain.objects.count()
        print(f"✅ Domain model working - {domain_count} domains")
        
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def check_web_responses():
    """Test web endpoints."""
    print("\n🌐 Testing web endpoints...")
    base_url = "http://localhost:8899"
    
    endpoints = [
        "/",
        "/admin/",
        "/dashboard/",
        "/api/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5, allow_redirects=False)
            if response.status_code in [200, 302]:
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def check_authentication():
    """Test authentication system."""
    print("\n🔐 Testing authentication...")
    try:
        # Check if we can create a user
        test_user = User.objects.create(username="test_user", is_active=True)
        print("✅ User creation successful")
        
        # Test custom auth methods
        print(f"✅ User has_usable_password: {test_user.has_usable_password()}")
        
        # Cleanup
        test_user.delete()
        print("✅ User cleanup successful")
        
        return True
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def check_migrations():
    """Check migration status."""
    print("\n📋 Checking migrations...")
    try:
        from django.core.management.commands.showmigrations import Command
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        unapplied = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if unapplied:
            print(f"⚠️  {len(unapplied)} unapplied migrations found")
            for migration, backwards in unapplied[:5]:  # Show first 5
                print(f"   - {migration}")
            return False
        else:
            print("✅ All migrations applied")
            return True
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

def main():
    """Run all validation checks."""
    print("FastCP Django 5.x Upgrade Validation")
    print("=" * 40)
    
    checks = [
        check_database_connection,
        check_migrations,
        check_models,
        check_authentication,
        check_web_responses,
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print(f"\n📊 Validation Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! FastCP upgrade validation successful.")
        sys.exit(0)
    else:
        print("⚠️  Some checks failed. Please review the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
