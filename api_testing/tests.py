from unittest.mock import MagicMock, patch

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from projects.models import Project

from .models import ApiTestRecord
from .services import ApiDebugService


class ApiDebugServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass123456", role=UserRole.TEST)

    @patch("api_testing.services.request.urlopen")
    def test_http_debug_auto_injects_platform_headers(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b'{"ok": true}'
        response.status = 200
        response.headers.items.return_value = [("Content-Type", "application/json")]
        response.__enter__.return_value = response
        mock_urlopen.return_value = response

        service = ApiDebugService(self.user)
        result = service.execute(
            {
                "protocol": "HTTP",
                "method": "GET",
                "target": "https://example.com/api",
                "headers": "{}",
                "request_payload": "",
            }
        )

        self.assertTrue(result["is_success"])
        self.assertIn("X-Platform-Auth", result["headers"])
        self.assertIn("X-Platform-User", result["headers"])

    @patch("api_testing.services.socket.create_connection")
    def test_tcp_debug_returns_hex_payload(self, mock_connection):
        fake_socket = MagicMock()
        fake_socket.recv.side_effect = [b"\x01\x02ABC", b""]
        mock_connection.return_value.__enter__.return_value = fake_socket

        service = ApiDebugService(self.user)
        result = service.execute(
            {
                "protocol": "TCP",
                "method": "",
                "target": "127.0.0.1:9000",
                "headers": "",
                "request_payload": "ping",
            }
        )

        self.assertTrue(result["is_success"])
        self.assertEqual(result["response_hex"], "01 02 41 42 43")


class ApiDebugViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="pass123456", role=UserRole.TEST)
        self.project = Project.objects.create(name="API", code="API")

    @patch("api_testing.services.request.urlopen")
    def test_post_debug_request_creates_record(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"ok"
        response.status = 200
        response.headers.items.return_value = []
        response.__enter__.return_value = response
        mock_urlopen.return_value = response

        self.client.login(username="tester", password="pass123456")
        response = self.client.post(
            reverse("api_testing:collection-list"),
            {
                "project": self.project.id,
                "name": "HTTP smoke",
                "protocol": "HTTP",
                "method": "GET",
                "target": "https://example.com/ping",
                "headers": "{}",
                "request_payload": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ApiTestRecord.objects.count(), 1)
