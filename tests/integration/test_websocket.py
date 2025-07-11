import asyncio
import json
from unittest import TestCase

from api.consumers import MetricsConsumer, StatusConsumer


class WebSocketConsumerTest(TestCase):
    """Unit tests for WebSocket consumer functionality"""

    def test_websocket_url_routing(self):
        """Test that WebSocket URLs are properly configured"""
        from api.routing import websocket_urlpatterns

        self.assertEqual(len(websocket_urlpatterns), 2)

        # Check that routes are defined
        route_patterns = [str(route.pattern) for route in websocket_urlpatterns]
        self.assertTrue(any("metrics" in pattern for pattern in route_patterns))
        self.assertTrue(any("status" in pattern for pattern in route_patterns))

    def test_metrics_consumer_has_required_methods(self):
        """Test that MetricsConsumer has all required methods"""
        consumer = MetricsConsumer()

        self.assertTrue(hasattr(consumer, "connect"))
        self.assertTrue(hasattr(consumer, "disconnect"))
        self.assertTrue(hasattr(consumer, "get_metrics_data"))
        self.assertTrue(hasattr(consumer, "send_metrics_updates"))

    def test_status_consumer_has_required_methods(self):
        """Test that StatusConsumer has all required methods"""
        consumer = StatusConsumer()

        self.assertTrue(hasattr(consumer, "connect"))
        self.assertTrue(hasattr(consumer, "disconnect"))
        self.assertTrue(hasattr(consumer, "get_status_data"))
        self.assertTrue(hasattr(consumer, "send_status_updates"))
        self.assertTrue(hasattr(consumer, "test_database_connection"))
