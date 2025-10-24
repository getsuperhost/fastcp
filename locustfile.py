import json
from locust import HttpUser, task, between
from locust.exception import StopUser


class FastCPUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login to the application"""
        # First, get the login page to obtain CSRF token
        response = self.client.get("/dashboard/sign-in/")
        if response.status_code != 200:
            raise StopUser(f"Failed to get login page: {response.status_code}")

        # Extract CSRF token from the response
        import re
        csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        if not csrf_match:
            raise StopUser("CSRF token not found in login page")

        csrf_token = csrf_match.group(1)

        # Now login with CSRF token
        login_data = {
            "username": "testuser",
            "password": "testpass",
            "csrfmiddlewaretoken": csrf_token
        }

        response = self.client.post("/dashboard/sign-in/", login_data,
                                  headers={"Referer": self.host + "/dashboard/sign-in/"})
        if response.status_code not in [200, 302] or "login" in response.url.lower() or "sign-in" in response.url.lower():
            raise StopUser(f"Login failed: {response.status_code}, URL: {response.url}")

    @task
    def get_websites(self):
        """Get list of websites"""
        self.client.get("/api/websites/")

    @task(2)
    def get_databases(self):
        """Test getting list of databases"""
        self.client.get("/api/databases/")

    @task(2)
    def get_filemanager_root(self):
        """Test filemanager root directory listing"""
        self.client.get("/api/filemanager/?path=/")

    @task(1)
    def get_stats(self):
        """Test getting system stats"""
        self.client.get("/api/stats/")

    @task(1)
    def create_website_simulation(self):
        """Simulate website creation (without actually creating)"""
        # This is a simulation - in real load testing you'd use different domains
        # Comment out actual creation to avoid creating test sites
        # self.client.post("/api/websites/", json=payload)
        pass

    @task(1)
    def ssl_certificate_request_simulation(self):
        """Simulate SSL certificate request (high load operation)"""
        # This would normally test the SSL certificate generation endpoint
        # For safety, we'll just test the status endpoint
        self.client.get("/api/websites/ssl/status/")

    @task(1)
    def database_operations_simulation(self):
        """Simulate database operations"""
        # Test database listing and basic operations
        self.client.get("/api/databases/")
        # Could add create/delete operations with proper cleanup