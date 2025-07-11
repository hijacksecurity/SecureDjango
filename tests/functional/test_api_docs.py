import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class APIDocumentationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            # pragma: allowlist nextline secret
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_swagger_ui_endpoint(self):
        """Test that Swagger UI is accessible"""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "swagger-ui")

    def test_redoc_endpoint(self):
        """Test that ReDoc is accessible"""
        response = self.client.get("/api/redoc/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "redoc")

    def test_api_schema_endpoint(self):
        """Test that API schema is accessible"""
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/vnd.oai.openapi", response["Content-Type"])

    def test_api_schema_format(self):
        """Test that API schema has correct format"""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("json", response["Content-Type"])

        schema = response.json()
        self.assertIn("openapi", schema)
        self.assertIn("info", schema)
        self.assertIn("paths", schema)
        self.assertEqual(schema["info"]["title"], "MyApp API")
        self.assertEqual(schema["info"]["version"], "1.0.0")

    def test_api_schema_includes_endpoints(self):
        """Test that API schema includes our endpoints"""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()
        paths = schema["paths"]

        # Check that our main API endpoints are documented
        self.assertIn("/api/v1/posts/", paths)
        self.assertIn("/api/v1/comments/", paths)
        self.assertIn("/api/v1/users/", paths)

    def test_api_schema_post_operations(self):
        """Test that POST operations are documented"""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()
        post_paths = schema["paths"]["/api/v1/posts/"]

        # Check that CRUD operations are documented
        self.assertIn("get", post_paths)  # List
        self.assertIn("post", post_paths)  # Create

        # Check POST operation details
        post_operation = post_paths["post"]
        self.assertIn("operationId", post_operation)
        self.assertIn("requestBody", post_operation)
        self.assertIn("responses", post_operation)

    def test_api_schema_custom_actions(self):
        """Test that custom actions are documented"""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()

        # Check for custom publish/unpublish actions
        if "/api/v1/posts/{id}/publish/" in schema["paths"]:
            publish_path = schema["paths"]["/api/v1/posts/{id}/publish/"]
            self.assertIn("post", publish_path)


class APIRootUpdatedTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_root_includes_documentation_links(self):
        """Test that API root includes documentation endpoints"""
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("endpoints", data)
        self.assertIn("swagger_docs", data["endpoints"])
        self.assertIn("redoc_docs", data["endpoints"])
        self.assertIn("api_schema", data["endpoints"])

        # Check the actual URLs
        self.assertEqual(data["endpoints"]["swagger_docs"], "/api/docs/")
        self.assertEqual(data["endpoints"]["redoc_docs"], "/api/redoc/")
        self.assertEqual(data["endpoints"]["api_schema"], "/api/schema/")

    def test_api_root_includes_websocket_endpoints(self):
        """Test that API root includes WebSocket endpoints"""
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("websocket_endpoints", data)
        self.assertIn("metrics", data["websocket_endpoints"])
        self.assertIn("status", data["websocket_endpoints"])


class HomePageUpdatedTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_includes_websocket_features(self):
        """Test that home page includes WebSocket features"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Check for WebSocket-related content
        self.assertContains(response, "Real-time")
        self.assertContains(response, "WebSocket")
        self.assertContains(response, "toggle-realtime-metrics")
        self.assertContains(response, "toggle-realtime-status")

    def test_home_page_includes_api_documentation_links(self):
        """Test that home page includes API documentation links"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Check for API documentation links
        self.assertContains(response, "/api/docs/")
        self.assertContains(response, "/api/redoc/")
        self.assertContains(response, "Swagger UI")
        self.assertContains(response, "ReDoc")

    def test_home_page_websocket_javascript(self):
        """Test that home page includes WebSocket JavaScript"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Check for WebSocket JavaScript functions
        self.assertContains(response, "new WebSocket")
        self.assertContains(response, "connectMetrics")
        self.assertContains(response, "connectStatus")
        self.assertContains(response, "updateMetrics")
        self.assertContains(response, "updateStatus")

    def test_home_page_updated_features_list(self):
        """Test that home page shows updated features"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Check for updated features
        self.assertContains(response, "WebSocket real-time updates")
        self.assertContains(response, "REST API with Swagger docs")


class WebSocketRoutingTest(TestCase):
    def test_websocket_routing_configuration(self):
        """Test that WebSocket routing is properly configured"""
        from api.routing import websocket_urlpatterns

        # Check that WebSocket routes are defined
        self.assertEqual(len(websocket_urlpatterns), 2)

        # Check route patterns
        route_patterns = [route.pattern._route for route in websocket_urlpatterns]
        self.assertIn("ws/metrics/", route_patterns)
        self.assertIn("ws/status/", route_patterns)
