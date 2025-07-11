"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from api import views as api_views

urlpatterns = [
    path("", api_views.home, name="home"),
    path("ws-test/", api_views.ws_test, name="ws-test"),
    path("admin/", admin.site.urls),
    path("health/", api_views.health_check, name="health-check"),
    path("status/", api_views.status, name="status"),
    path("metrics/", api_views.metrics, name="metrics"),
    path("prometheus/", api_views.prometheus_metrics, name="prometheus-metrics"),
    path("demo-lb/", api_views.demo_lb, name="demo-lb"),
    path("api/", include("api.urls")),
]
