#!/usr/bin/env python3
"""
FastCP Performance Testing Script
Tests key components for performance bottlenecks
"""

import time
import sys
import os
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastcp.settings')
import django
django.setup()

from api.websites.services.ssl import FastcpSsl
from api.websites.services.fcp_acme import FastcpAcme
import tempfile
import shutil


class PerformanceTester:
    def __init__(self):
        self.results = {}
        self.temp_dir = tempfile.mkdtemp(prefix='fastcp_perf_')

    def cleanup(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)
        start_memory = psutil.virtual_memory().used

        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = str(e)
            success = False

        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=None)
        end_memory = psutil.virtual_memory().used

        return {
            'execution_time': end_time - start_time,
            'cpu_usage': end_cpu - start_cpu,
            'memory_delta': end_memory - start_memory,
            'success': success,
            'result': result
        }

    def test_ssl_service_initialization(self):
        """Test SSL service initialization performance"""
        print("Testing SSL service initialization...")
        result = self.measure_time(FastcpSsl)
        self.results['ssl_init'] = result
        print(".2f")
        return result

    def test_filesystem_operations(self):
        """Test filesystem operations performance"""
        print("Testing filesystem operations...")

        # Create test directory
        test_dir = os.path.join(self.temp_dir, 'test_fs')
        
        # Test directory creation
        create_result = self.measure_time(
            os.makedirs,
            test_dir,
            exist_ok=True
        )

        # Test file operations
        test_file = os.path.join(test_dir, 'test.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('test content')

        def read_file_operation():
            with open(test_file, 'r', encoding='utf-8') as f:
                return f.read()

        read_result = self.measure_time(read_file_operation)

        self.results['fs_create'] = create_result
        self.results['fs_read'] = read_result

        print(".2f")
        print(".2f")

        return create_result, read_result

    def test_concurrent_operations(self):
        """Test concurrent operations"""
        print("Testing concurrent filesystem operations...")

        def create_file_worker(worker_id):
            test_file = os.path.join(self.temp_dir, f'concurrent_test_{worker_id}.txt')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f'Content from worker {worker_id}')
            return test_file

        # Test with 10 concurrent workers
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_file_worker, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]

        end_time = time.time()

        concurrent_result = {
            'execution_time': end_time - start_time,
            'success': True,
            'workers': 10,
            'files_created': len(results)
        }

        self.results['concurrent_fs'] = concurrent_result
        print(".2f")

        return concurrent_result

    def run_all_tests(self):
        """Run all performance tests"""
        print("=" * 60)
        print("FastCP Performance Testing Suite")
        print("=" * 60)

        try:
            # Run individual tests
            self.test_ssl_service_initialization()
            self.test_filesystem_operations()
            self.test_concurrent_operations()

            # Summary
            print("\n" + "=" * 60)
            print("PERFORMANCE TEST SUMMARY")
            print("=" * 60)

            total_tests = len(self.results)
            successful_tests = sum(1 for r in self.results.values() if r['success'])
            total_time = sum(r['execution_time'] for r in self.results.values())

            print(f"Total Tests: {total_tests}")
            print(f"Successful: {successful_tests}")
            print(f"Failed: {total_tests - successful_tests}")
            print(".2f")
            print(".2f")

            # Performance recommendations
            print("\nRECOMMENDATIONS:")
            if total_time > 5.0:
                print("- Consider optimizing initialization times")
            if any(r.get('cpu_usage', 0) > 50 for r in self.results.values()):
                print("- High CPU usage detected - monitor resource usage")
            if any(r.get('memory_delta', 0) > 50 * 1024 * 1024 for r in self.results.values()):  # 50MB
                print("- Significant memory usage - check for memory leaks")

            print("\nAll tests completed successfully!")

        except Exception as e:
            print(f"Error during testing: {str(e)}")
        finally:
            self.cleanup()


def main():
    tester = PerformanceTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()