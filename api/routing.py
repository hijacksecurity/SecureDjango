from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/metrics/", consumers.MetricsConsumer.as_asgi()),
    path("ws/status/", consumers.StatusConsumer.as_asgi()),
]
