"""
Test URL versioning consistency and accuracy.
"""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class URLVersioningTest(TestCase):
    """Test that URL versioning is consistent and accurate."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            # pragma: allowlist nextline secret
            password="testpass123",
        )

    def test_api_root_shows_versioned_urls(self):
        """Test that API root shows correct versioned URLs."""
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Check that API root includes version in resource URLs
        self.assertIn("api_v1_resources", data)
        resources = data["api_v1_resources"]

        # Verify all resources have v1 prefix
        expected_resources = {
            "posts": "/api/v1/posts/",
            "comments": "/api/v1/comments/",
            "users": "/api/v1/users/",
        }

        for resource, expected_url in expected_resources.items():
            self.assertIn(resource, resources)
            self.assertEqual(resources[resource], expected_url)

    def test_api_schema_shows_versioned_urls(self):
        """Test that API schema shows correct versioned URLs."""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()
        paths = schema.get("paths", {})

        # Check that all paths include version
        versioned_paths = [
            "/api/v1/posts/",
            "/api/v1/posts/{id}/",
            "/api/v1/posts/{id}/publish/",
            "/api/v1/posts/{id}/unpublish/",
            "/api/v1/comments/",
            "/api/v1/comments/{id}/",
            "/api/v1/users/",
            "/api/v1/users/{id}/",
        ]

        for path in versioned_paths:
            self.assertIn(path, paths, f"Missing versioned path: {path}")

        # Check that non-versioned paths don't exist
        non_versioned_paths = [
            "/api/posts/",
            "/api/comments/",
            "/api/users/",
        ]

        for path in non_versioned_paths:
            self.assertNotIn(path, paths, f"Found non-versioned path: {path}")

    def test_actual_endpoints_are_versioned(self):
        """Test that actual endpoints are accessible with versioned URLs."""
        # Test that versioned URLs work
        versioned_urls = [
            "/api/v1/posts/",
            "/api/v1/comments/",
            "/api/v1/users/",
        ]

        for url in versioned_urls:
            response = self.client.get(url)
            # Should be 200 (success) or 403 (forbidden due to permissions)
            # Both are valid - means the URL exists
            self.assertIn(
                response.status_code,
                [200, 403],
                f"Versioned URL {url} should be accessible",
            )

    def test_non_versioned_endpoints_dont_exist(self):
        """Test that non-versioned URLs return 404."""
        non_versioned_urls = [
            "/api/posts/",
            "/api/comments/",
            "/api/users/",
        ]

        for url in non_versioned_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, 404, f"Non-versioned URL {url} should return 404"
            )

    def test_api_version_in_schema_info(self):
        """Test that API version is correctly shown in schema info."""
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)

        schema = response.json()
        info = schema.get("info", {})

        # Check version is present and correct
        self.assertIn("version", info)
        self.assertEqual(info["version"], "1.0.0")

        # Check title and description
        self.assertEqual(info["title"], "MyApp API")
        self.assertIn("Production-ready Django REST API", info["description"])

    def test_swagger_ui_shows_correct_version(self):
        """Test that Swagger UI shows the correct version."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)

        # Check that the HTML contains version information
        content = response.content.decode()
        self.assertIn("MyApp API", content)

    def test_api_root_version_consistency(self):
        """Test that API root version matches schema version."""
        # Get version from API root
        root_response = self.client.get("/api/")
        root_data = root_response.json()
        root_version = root_data.get("version")

        # Get version from schema
        schema_response = self.client.get("/api/schema/?format=json")
        schema_data = schema_response.json()
        schema_version = schema_data.get("info", {}).get("version")

        # Versions should match
        self.assertEqual(
            root_version, schema_version, "API root version should match schema version"
        )
        self.assertEqual(root_version, "1.0.0")

    def test_url_patterns_are_consistent(self):
        """Test that URL patterns are consistent across the application."""
        # Test that all v1 URLs follow the same pattern
        response = self.client.get("/api/schema/?format=json")
        schema = response.json()
        paths = schema.get("paths", {})

        # All API paths should start with /api/v1/
        api_paths = [path for path in paths.keys() if path.startswith("/api/")]

        for path in api_paths:
            self.assertTrue(
                path.startswith("/api/v1/"),
                f"API path {path} should start with /api/v1/",
            )

        # Check that we have the expected number of API paths
        self.assertGreaterEqual(
            len(api_paths), 8, "Should have at least 8 API endpoints"
        )

    def test_documentation_links_are_versioned_aware(self):
        """Test that documentation links point to versioned resources."""
        response = self.client.get("/api/")
        data = response.json()

        # Check that the API root mentions v1 resources
        self.assertIn("api_v1", data["endpoints"])
        self.assertEqual(data["endpoints"]["api_v1"], "/api/v1/")

        # Check that we have documentation endpoints
        doc_endpoints = ["swagger_docs", "redoc_docs", "api_schema"]
        for endpoint in doc_endpoints:
            self.assertIn(endpoint, data["endpoints"])

    def test_version_format_is_semver(self):
        """Test that version follows semantic versioning format."""
        response = self.client.get("/api/schema/?format=json")
        schema = response.json()
        version = schema.get("info", {}).get("version")

        # Check that version matches semver pattern (X.Y.Z)
        import re

        semver_pattern = r"^\d+\.\d+\.\d+$"
        self.assertRegex(
            version, semver_pattern, f"Version {version} should follow semver format"
        )
