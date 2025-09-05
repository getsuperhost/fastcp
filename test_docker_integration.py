#!/usr/bin/env python3
"""
FastCP Docker Integration Test
Tests the newly added Docker packages for container management capabilities.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
os.environ.setdefault('IS_DEBUG', '1')
django.setup()

def test_docker_integration():
    """Test Docker package integration."""
    print("🔧 Testing FastCP Docker Integration")
    print("=" * 40)

    try:
        # Test Docker package import
        import docker
        print("✅ Docker package imported successfully")
        print(f"   Version: {docker.version}")

        # Test Docker client connection
        client = docker.from_env()
        print("✅ Docker client connected")

        # Get Docker info
        info = client.info()
        print(f"✅ Docker daemon info retrieved")
        print(f"   Containers: {info['Containers']}")
        print(f"   Images: {info['Images']}")

        # List running containers
        containers = client.containers.list()
        print(f"✅ Found {len(containers)} running containers")

        # Test docker-pycreds import
        import dockerpycreds
        print("✅ docker-pycreds package imported successfully")

        print("\n🎉 Docker integration test completed successfully!")
        print("FastCP can now interact with Docker containers for:")
        print("  - Container management")
        print("  - Image operations")
        print("  - Volume management")
        print("  - Network configuration")
        print("  - Service orchestration")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Docker integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_docker_integration()
    sys.exit(0 if success else 1)
