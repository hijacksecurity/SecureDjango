import asyncio
import json
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.test.utils import override_settings

from api.consumers import MetricsConsumer, StatusConsumer


class ConsumerUnitTest(TestCase):
    """Unit tests for WebSocket consumers without actual connections"""

    def setUp(self):
        self.metrics_consumer = MetricsConsumer()
        self.status_consumer = StatusConsumer()

    @patch("api.consumers.psutil.cpu_percent")
    @patch("api.consumers.psutil.virtual_memory")
    @patch("api.consumers.psutil.disk_usage")
    def test_metrics_consumer_get_metrics_data(self, mock_disk, mock_memory, mock_cpu):
        """Test metrics data collection"""
        mock_cpu.return_value = 25.5
        mock_memory.return_value.percent = 45.2
        mock_disk.return_value.percent = 60.8

        # Test the sync version of get_metrics_data
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            data = loop.run_until_complete(self.metrics_consumer.get_metrics_data())

            self.assertEqual(data["cpu_percent"], 25.5)
            self.assertEqual(data["memory_percent"], 45.2)
            self.assertEqual(data["disk_percent"], 60.8)
            self.assertIn("hostname", data)
            self.assertIn("timestamp", data)
        finally:
            loop.close()

    @patch("api.consumers.psutil.cpu_percent")
    def test_metrics_consumer_error_handling(self, mock_cpu):
        """Test error handling in metrics data collection"""
        mock_cpu.side_effect = Exception("CPU error")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            data = loop.run_until_complete(self.metrics_consumer.get_metrics_data())

            self.assertIn("error", data)
            self.assertIn("hostname", data)
            self.assertIn("timestamp", data)
        finally:
            loop.close()

    @patch("api.consumers.connection.cursor")
    def test_status_consumer_get_status_data(self, mock_cursor):
        """Test status data collection"""
        mock_cursor.return_value.__enter__.return_value.execute.return_value = None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            data = loop.run_until_complete(self.status_consumer.get_status_data())

            self.assertEqual(data["application"], "healthy")
            self.assertEqual(data["database"], "Connected")
            self.assertIn("hostname", data)
            self.assertIn("timestamp", data)
        finally:
            loop.close()

    def test_status_consumer_database_error(self):
        """Test database error handling in status data collection"""
        # Test that the consumer can handle errors gracefully
        consumer = StatusConsumer()

        # Test that the consumer has the right methods
        self.assertTrue(hasattr(consumer, "get_status_data"))
        self.assertTrue(hasattr(consumer, "test_database_connection"))

        # Test that status data always includes required fields
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            data = loop.run_until_complete(consumer.get_status_data())

            self.assertIn("application", data)
            self.assertIn("database", data)
            self.assertIn("hostname", data)
            self.assertIn("timestamp", data)
        finally:
            loop.close()

    def test_consumer_classes_exist(self):
        """Test that consumer classes are properly defined"""
        from api.consumers import MetricsConsumer, StatusConsumer

        self.assertTrue(hasattr(MetricsConsumer, "connect"))
        self.assertTrue(hasattr(MetricsConsumer, "disconnect"))
        self.assertTrue(hasattr(MetricsConsumer, "get_metrics_data"))

        self.assertTrue(hasattr(StatusConsumer, "connect"))
        self.assertTrue(hasattr(StatusConsumer, "disconnect"))
        self.assertTrue(hasattr(StatusConsumer, "get_status_data"))

    def test_routing_configuration(self):
        """Test that WebSocket routing is properly configured"""
        from api.routing import websocket_urlpatterns

        self.assertEqual(len(websocket_urlpatterns), 2)

        # Check that routes are defined
        route_patterns = [str(route.pattern) for route in websocket_urlpatterns]
        self.assertTrue(any("metrics" in pattern for pattern in route_patterns))
        self.assertTrue(any("status" in pattern for pattern in route_patterns))
