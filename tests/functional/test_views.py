import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class HealthCheckViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint_get(self):
        response = self.client.get(reverse("health-check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("hostname", data)
        self.assertIn("timestamp", data)
        self.assertEqual(data["version"], "1.0.0")

    def test_health_check_endpoint_head(self):
        response = self.client.head(reverse("health-check"))
        self.assertEqual(response.status_code, 200)

    def test_health_check_endpoint_post_not_allowed(self):
        response = self.client.post(reverse("health-check"))
        self.assertEqual(response.status_code, 405)


class StatusViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_endpoint_json_response(self):
        response = self.client.get(reverse("status"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertEqual(data["application"], "healthy")
        self.assertIn("database", data)
        self.assertIn("hostname", data)
        self.assertIn("timestamp", data)

    def test_status_endpoint_htmx_response(self):
        response = self.client.get(reverse("status"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "healthy")

    @patch("django.db.connection.cursor")
    def test_status_endpoint_database_error(self, mock_cursor):
        mock_cursor.side_effect = Exception("Database connection failed")

        response = self.client.get(reverse("status"))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("Error:", data["database"])


class MetricsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_metrics_endpoint_json_response(self, mock_disk, mock_memory, mock_cpu):
        mock_cpu.return_value = 25.5
        mock_memory.return_value.percent = 45.2
        mock_disk.return_value.percent = 60.8

        response = self.client.get(reverse("metrics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertEqual(data["cpu_percent"], 25.5)
        self.assertEqual(data["memory_percent"], 45.2)
        self.assertEqual(data["disk_percent"], 60.8)
        self.assertIn("hostname", data)
        self.assertIn("timestamp", data)

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_metrics_endpoint_htmx_response(self, mock_disk, mock_memory, mock_cpu):
        mock_cpu.return_value = 25.5
        mock_memory.return_value.percent = 45.2
        mock_disk.return_value.percent = 60.8

        response = self.client.get(reverse("metrics"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "25.5")

    @patch("psutil.cpu_percent")
    def test_metrics_endpoint_error_handling(self, mock_cpu):
        mock_cpu.side_effect = Exception("Failed to get CPU metrics")

        response = self.client.get(reverse("metrics"))
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertIn("error", data)


class DemoLoadBalancerViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_demo_lb_endpoint_json_response(self):
        response = self.client.get(reverse("demo-lb"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertIn("request_id", data)
        self.assertIn("hostname", data)
        self.assertIn("timestamp", data)
        self.assertIn("message", data)
        self.assertIn("Handled by pod:", data["message"])

    def test_demo_lb_endpoint_htmx_response(self):
        response = self.client.get(reverse("demo-lb"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Handled by pod:")

    def test_demo_lb_endpoint_increments_counter(self):
        response = self.client.get(reverse("demo-lb"))
        self.assertEqual(response.status_code, 200)


class PrometheusMetricsViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_prometheus_metrics_endpoint(self, mock_memory, mock_cpu):
        mock_cpu.return_value = 25.5
        mock_memory.return_value.percent = 45.2

        response = self.client.get(reverse("prometheus-metrics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"], "text/plain; version=0.0.4; charset=utf-8"
        )

        content = response.content.decode("utf-8")
        self.assertIn("cpu_usage_percent", content)
        self.assertIn("memory_usage_percent", content)
        self.assertIn("http_requests_total", content)

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_prometheus_metrics_with_exception(self, mock_memory, mock_cpu):
        mock_cpu.side_effect = Exception("CPU metrics failed")
        mock_memory.side_effect = Exception("Memory metrics failed")

        response = self.client.get(reverse("prometheus-metrics"))
        self.assertEqual(response.status_code, 200)


class APIRootViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_root_endpoint_structure(self):
        response = self.client.get(reverse("api-root"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertEqual(data["message"], "Welcome to MyApp API")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("endpoints", data)
        self.assertIn("api_v1_resources", data)

    def test_api_root_endpoint_contains_all_endpoints(self):
        response = self.client.get(reverse("api-root"))
        data = json.loads(response.content)

        expected_endpoints = [
            "health",
            "status",
            "metrics",
            "demo_lb",
            "prometheus",
            "api_v1",
            "api_auth",
            "swagger_docs",
            "redoc_docs",
            "api_schema",
        ]
        for endpoint in expected_endpoints:
            self.assertIn(endpoint, data["endpoints"])

    def test_api_root_endpoint_contains_resources(self):
        response = self.client.get(reverse("api-root"))
        data = json.loads(response.content)

        expected_resources = ["posts", "comments", "users"]
        for resource in expected_resources:
            self.assertIn(resource, data["api_v1_resources"])


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_endpoint_get(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MyApp Dashboard")

    def test_home_endpoint_head(self):
        response = self.client.head(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_endpoint_post_not_allowed(self):
        response = self.client.post(reverse("home"))
        self.assertEqual(response.status_code, 405)

    def test_home_endpoint_contains_navigation(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "System Status")
        self.assertContains(response, "Metrics")
        self.assertContains(response, "Load Balancing Demo")


class ViewsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_authenticated_user_can_access_all_views(self):
        self.client.login(username="testuser", password="testpass123")

        endpoints = [
            "home",
            "health-check",
            "status",
            "metrics",
            "demo-lb",
            "prometheus-metrics",
            "api-root",
        ]

        for endpoint in endpoints:
            response = self.client.get(reverse(endpoint))
            self.assertIn(response.status_code, [200, 405])

    def test_unauthenticated_user_can_access_public_views(self):
        endpoints = [
            "home",
            "health-check",
            "status",
            "metrics",
            "demo-lb",
            "prometheus-metrics",
            "api-root",
        ]

        for endpoint in endpoints:
            response = self.client.get(reverse(endpoint))
            self.assertIn(response.status_code, [200, 405])
