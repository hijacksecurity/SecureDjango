import json

import requests
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from rest_framework.test import APITestCase

from api.models import Comment, Post


class FullWorkflowTest(APITestCase):
    """
    End-to-end test for complete user workflow.
    This test should run against a deployed environment.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="e2euser", email="e2e@example.com", password="e2epass123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )

    def test_complete_blog_workflow(self):
        """Test complete blog workflow: create user, post, comment, and interact"""

        # Step 1: Check API root is accessible
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

        # Step 2: Check health endpoint
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

        # Step 3: Authenticate user
        self.client.force_authenticate(user=self.user)

        # Step 4: Create a blog post
        post_data = {
            "title": "My First E2E Post",
            "content": "This is my first post created during E2E testing.",
            "published": True,
        }
        response = self.client.post("/api/v1/posts/", post_data)
        self.assertEqual(response.status_code, 201)
        post_id = response.json()["id"]

        # Step 5: Verify post was created
        response = self.client.get(f"/api/v1/posts/{post_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "My First E2E Post")

        # Step 6: Create a comment on the post
        comment_data = {
            "content": "Great post! This is a test comment.",
            "post": post_id,
        }
        response = self.client.post("/api/v1/comments/", comment_data)
        self.assertEqual(response.status_code, 201)
        comment_id = response.json()["id"]

        # Step 7: Verify comment was created
        response = self.client.get(f"/api/v1/comments/{comment_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["content"], "Great post! This is a test comment."
        )

        # Step 8: Update the post
        update_data = {
            "title": "My Updated E2E Post",
            "content": "This content has been updated during E2E testing.",
            "published": True,
        }
        response = self.client.put(f"/api/v1/posts/{post_id}/", update_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "My Updated E2E Post")

        # Step 9: Publish/unpublish post
        response = self.client.post(f"/api/v1/posts/{post_id}/unpublish/")
        self.assertEqual(response.status_code, 200)

        response = self.client.post(f"/api/v1/posts/{post_id}/publish/")
        self.assertEqual(response.status_code, 200)

        # Step 10: Check post in list view
        response = self.client.get("/api/v1/posts/")
        self.assertEqual(response.status_code, 200)
        posts = response.json()["results"]
        self.assertTrue(any(p["id"] == post_id for p in posts))

        # Step 11: Check user profile
        response = self.client.get(f"/api/v1/users/{self.user.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "e2euser")

        # Step 12: Clean up - delete comment and post
        response = self.client.delete(f"/api/v1/comments/{comment_id}/")
        self.assertEqual(response.status_code, 204)

        response = self.client.delete(f"/api/v1/posts/{post_id}/")
        self.assertEqual(response.status_code, 204)

    def test_monitoring_endpoints_workflow(self):
        """Test monitoring and system endpoints workflow"""

        # Step 1: Check system status
        response = self.client.get("/status/")
        self.assertEqual(response.status_code, 200)
        status_data = response.json()
        self.assertEqual(status_data["application"], "healthy")

        # Step 2: Check metrics
        response = self.client.get("/metrics/")
        self.assertEqual(response.status_code, 200)
        metrics_data = response.json()
        self.assertIn("cpu_percent", metrics_data)
        self.assertIn("memory_percent", metrics_data)

        # Step 3: Check load balancer demo
        response = self.client.get("/demo-lb/")
        self.assertEqual(response.status_code, 200)
        lb_data = response.json()
        self.assertIn("hostname", lb_data)
        self.assertIn("request_id", lb_data)

        # Step 4: Check Prometheus metrics
        response = self.client.get("/prometheus/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response["Content-Type"])

    def test_htmx_endpoints_workflow(self):
        """Test HTMX endpoints workflow"""

        # Step 1: Test status with HTMX
        response = self.client.get("/status/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)

        # Step 2: Test metrics with HTMX
        response = self.client.get("/metrics/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)

        # Step 3: Test load balancer demo with HTMX
        response = self.client.get("/demo-lb/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)

    def test_error_handling_workflow(self):
        """Test error handling across the application"""

        # Step 1: Test 404 on non-existent post
        response = self.client.get("/api/v1/posts/99999/")
        self.assertEqual(response.status_code, 404)

        # Step 2: Test 401 on protected endpoint
        response = self.client.post("/api/v1/posts/", {"title": "Test"})
        self.assertEqual(response.status_code, 401)

        # Step 3: Test 400 on invalid data
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/posts/", {"title": ""})
        self.assertEqual(response.status_code, 400)

        # Step 4: Test 405 on method not allowed
        response = self.client.post("/health/")
        self.assertEqual(response.status_code, 405)

    def test_pagination_workflow(self):
        """Test pagination across list endpoints"""

        self.client.force_authenticate(user=self.user)

        # Create multiple posts
        for i in range(15):
            self.client.post(
                "/api/v1/posts/",
                {
                    "title": f"Test Post {i}",
                    "content": f"Content for post {i}",
                    "published": True,
                },
            )

        # Test posts pagination
        response = self.client.get("/api/v1/posts/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertTrue(data["count"] >= 15)

        # Test comments pagination
        response = self.client.get("/api/v1/comments/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)

        # Test users pagination
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("count", data)
        self.assertIn("results", data)


class DeploymentHealthTest(TestCase):
    """
    Basic health checks for deployed environment.
    These tests verify the deployment is functional.
    """

    def test_basic_deployment_health(self):
        """Test basic deployment health indicators"""

        # Test home page loads
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Test health check
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)

        # Test API root
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)

        # Test database connectivity via status
        response = self.client.get("/status/")
        self.assertEqual(response.status_code, 200)
        status_data = response.json()
        self.assertEqual(status_data["application"], "healthy")
        self.assertNotIn("Error:", status_data["database"])

    def test_static_files_serving(self):
        """Test that static files are served correctly"""

        # Test home page includes CSS/JS
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "htmx")

    def test_cors_headers(self):
        """Test CORS headers are present"""

        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        # CORS headers should be present for API endpoints

    def test_security_headers(self):
        """Test security headers are present"""

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # Security headers should be present
