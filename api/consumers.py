import asyncio
import json
import socket
from datetime import datetime

import psutil
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import connection


class MetricsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("metrics", self.channel_name)
        await self.accept()

        # Start sending metrics updates
        self.metrics_task = asyncio.create_task(self.send_metrics_updates())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("metrics", self.channel_name)

        # Cancel the metrics task
        if hasattr(self, "metrics_task"):
            self.metrics_task.cancel()

    async def send_metrics_updates(self):
        """Send metrics updates every 5 seconds"""
        while True:
            try:
                metrics_data = await self.get_metrics_data()
                await self.send(
                    text_data=json.dumps(
                        {"type": "metrics_update", "data": metrics_data}
                    )
                )
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.send(
                    text_data=json.dumps(
                        {"type": "error", "message": f"Error getting metrics: {str(e)}"}
                    )
                )
                await asyncio.sleep(5)

    async def get_metrics_data(self):
        """Get current system metrics"""
        try:
            # Get system metrics
            cpu_percent = await sync_to_async(psutil.cpu_percent)(interval=1)
            memory = await sync_to_async(psutil.virtual_memory)()
            disk = await sync_to_async(psutil.disk_usage)("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "hostname": socket.gethostname(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "hostname": socket.gethostname(),
                "timestamp": datetime.now().isoformat(),
            }


class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("status", self.channel_name)
        await self.accept()

        # Start sending status updates
        self.status_task = asyncio.create_task(self.send_status_updates())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("status", self.channel_name)

        # Cancel the status task
        if hasattr(self, "status_task"):
            self.status_task.cancel()

    async def send_status_updates(self):
        """Send status updates every 10 seconds"""
        while True:
            try:
                status_data = await self.get_status_data()
                await self.send(
                    text_data=json.dumps({"type": "status_update", "data": status_data})
                )
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.send(
                    text_data=json.dumps(
                        {"type": "error", "message": f"Error getting status: {str(e)}"}
                    )
                )
                await asyncio.sleep(10)

    async def get_status_data(self):
        """Get current system status"""
        try:
            # Test database connection
            db_status = await self.test_database_connection()

            return {
                "application": "healthy",
                "database": db_status,
                "hostname": socket.gethostname(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "application": "error",
                "database": f"Error: {str(e)[:50]}",
                "hostname": socket.gethostname(),
                "timestamp": datetime.now().isoformat(),
            }

    async def test_database_connection(self):
        """Test database connection asynchronously"""
        try:

            @sync_to_async
            def test_db():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return "Connected"

            return await test_db()
        except Exception as e:
            return f"Error: {str(e)[:50]}"
