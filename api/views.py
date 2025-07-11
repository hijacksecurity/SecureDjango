import socket
import time
from datetime import datetime

import psutil
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint"]
)
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
ACTIVE_CONNECTIONS = Gauge("active_connections", "Number of active connections")
CPU_USAGE = Gauge("cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Memory usage percentage")


@require_http_methods(["GET", "HEAD"])
def home(request):
    return render(request, "index.html")


@require_http_methods(["GET"])
def ws_test(request):
    """WebSocket test page"""
    return render(request, "ws-test.html")


@require_http_methods(["GET", "HEAD"])
def health_check(request):
    return JsonResponse(
        {
            "status": "healthy",
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        },
        status=200,
    )


@require_http_methods(["GET"])
def api_root(request):
    return JsonResponse(
        {
            "message": "Welcome to MyApp API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health/",
                "status": "/status/",
                "metrics": "/metrics/",
                "demo_lb": "/demo-lb/",
                "prometheus": "/prometheus/",
                "api_v1": "/api/v1/",
                "api_auth": "/api/auth/",
                "swagger_docs": "/api/docs/",
                "redoc_docs": "/api/redoc/",
                "api_schema": "/api/schema/",
            },
            "api_v1_resources": {
                "posts": "/api/v1/posts/",
                "comments": "/api/v1/comments/",
                "users": "/api/v1/users/",
            },
            "websocket_endpoints": {
                "metrics": "ws://localhost:8000/ws/metrics/",
                "status": "ws://localhost:8000/ws/status/",
            },
        }
    )


@require_http_methods(["GET"])
def status(request):
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)[:50]}"

    status_data = {
        "application": "healthy",
        "database": db_status,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
    }

    # Return HTML for HTMX, JSON for API
    if request.headers.get("HX-Request"):
        return render(request, "status.html", {"status": status_data})
    return JsonResponse(status_data)


@require_http_methods(["GET"])
def metrics(request):
    try:
        # Get basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        metrics_data = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
        }

        # Return HTML for HTMX, JSON for API
        if request.headers.get("HX-Request"):
            return render(request, "metrics.html", {"metrics": metrics_data})
        return JsonResponse(metrics_data)
    except Exception as e:
        error_data = {
            "error": str(e),
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
        }
        return JsonResponse(error_data)


@require_http_methods(["GET"])
def demo_lb(request):
    REQUEST_COUNT.labels(method="GET", endpoint="demo_lb").inc()

    lb_data = {
        "request_id": int(time.time() * 1000),
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": f"Handled by pod: {socket.gethostname()}",
    }

    # Return HTML for HTMX, JSON for API
    if request.headers.get("HX-Request"):
        return render(request, "demo_lb.html", {"lb": lb_data})
    return JsonResponse(lb_data)


@require_http_methods(["GET"])
def prometheus_metrics(request):
    # Update metrics
    try:
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        CPU_USAGE.set(cpu_percent)
        MEMORY_USAGE.set(memory_percent)
    except:
        pass

    REQUEST_COUNT.labels(method="GET", endpoint="prometheus_metrics").inc()

    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


from django.contrib.auth.models import User

# REST API ViewSets
from rest_framework import permissions
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Comment, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CommentSerializer,
    PostListSerializer,
    PostSerializer,
    UserSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    Simple CRUD API for blog posts

    Available endpoints:
    - GET /api/v1/posts/ - List all posts
    - POST /api/v1/posts/ - Create a new post
    - GET /api/v1/posts/{id}/ - Get a specific post
    - PUT/PATCH /api/v1/posts/{id}/ - Update a post
    - DELETE /api/v1/posts/{id}/ - Delete a post
    """

    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publish a post"""
        post = self.get_object()
        post.published = True
        post.save()
        return Response({"status": "post published"})

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        """Unpublish a post"""
        post = self.get_object()
        post.published = False
        post.save()
        return Response({"status": "post unpublished"})


class CommentViewSet(viewsets.ModelViewSet):
    """
    Simple CRUD API for comments

    Available endpoints:
    - GET /api/v1/comments/ - List all comments
    - POST /api/v1/comments/ - Create a new comment
    - GET /api/v1/comments/{id}/ - Get a specific comment
    - PUT/PATCH /api/v1/comments/{id}/ - Update a comment
    - DELETE /api/v1/comments/{id}/ - Delete a comment
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for users

    Available endpoints:
    - GET /api/v1/users/ - List all users
    - GET /api/v1/users/{id}/ - Get a specific user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
