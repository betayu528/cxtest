import asyncio
import json
import socket
import time
from urllib import error, parse, request

from django.conf import settings

from .models import ApiProtocol

try:
    import websockets
except ImportError:  # pragma: no cover
    websockets = None


def platform_auth_headers(user):
    username = user.username if user and user.is_authenticated else "anonymous"
    role = getattr(user, "role", "GUEST") if user and user.is_authenticated else "GUEST"
    return {
        settings.PLATFORM_INTERNAL_AUTH_HEADER: settings.PLATFORM_INTERNAL_AUTH_TOKEN,
        settings.PLATFORM_INTERNAL_USER_HEADER: username,
        settings.PLATFORM_INTERNAL_ROLE_HEADER: role,
    }


class ApiDebugService:
    def __init__(self, user=None):
        self.user = user

    def execute(self, cleaned_data):
        protocol = cleaned_data["protocol"]
        if protocol == ApiProtocol.HTTP:
            return self._execute_http(cleaned_data)
        if protocol == ApiProtocol.TCP:
            return self._execute_tcp(cleaned_data)
        if protocol == ApiProtocol.WEBSOCKET:
            return self._execute_websocket(cleaned_data)
        raise ValueError(f"unsupported protocol: {protocol}")

    def _parse_headers(self, raw_headers):
        if not raw_headers:
            return {}
        try:
            parsed = json.loads(raw_headers)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _execute_http(self, cleaned_data):
        started = time.perf_counter()
        headers = self._parse_headers(cleaned_data["headers"])
        headers.update(platform_auth_headers(self.user))
        payload = cleaned_data["request_payload"]
        data = payload.encode("utf-8") if payload and cleaned_data["method"] in {"POST", "PUT", "PATCH", "DELETE"} else None
        req = request.Request(cleaned_data["target"], data=data, headers=headers, method=cleaned_data["method"] or "GET")
        try:
            with request.urlopen(req, timeout=15) as response:
                response_bytes = response.read()
                response_text = response_bytes.decode("utf-8", errors="replace")
                return {
                    "protocol": ApiProtocol.HTTP,
                    "method": cleaned_data["method"] or "GET",
                    "headers": headers,
                    "response_status": str(response.status),
                    "response_headers": dict(response.headers.items()),
                    "response_text": response_text,
                    "response_hex": response_bytes.hex(" "),
                    "duration_ms": int((time.perf_counter() - started) * 1000),
                    "is_success": True,
                    "error_message": "",
                }
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return {
                "protocol": ApiProtocol.HTTP,
                "method": cleaned_data["method"] or "GET",
                "headers": headers,
                "response_status": str(exc.code),
                "response_headers": dict(exc.headers.items()),
                "response_text": body,
                "response_hex": body.encode("utf-8").hex(" "),
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "is_success": False,
                "error_message": str(exc),
            }
        except Exception as exc:
            return {
                "protocol": ApiProtocol.HTTP,
                "method": cleaned_data["method"] or "GET",
                "headers": headers,
                "response_status": "",
                "response_headers": {},
                "response_text": "",
                "response_hex": "",
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "is_success": False,
                "error_message": str(exc),
            }

    def _execute_tcp(self, cleaned_data):
        started = time.perf_counter()
        parsed = parse.urlparse(cleaned_data["target"] if "://" in cleaned_data["target"] else f"tcp://{cleaned_data['target']}")
        host = parsed.hostname
        port = parsed.port
        payload = cleaned_data["request_payload"].encode("utf-8")
        response_bytes = b""
        try:
            with socket.create_connection((host, port), timeout=10) as sock:
                sock.sendall(payload)
                sock.shutdown(socket.SHUT_WR)
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_bytes += chunk
            return {
                "protocol": ApiProtocol.TCP,
                "method": "",
                "headers": {},
                "response_status": "TCP_OK",
                "response_headers": {},
                "response_text": response_bytes.decode("utf-8", errors="replace"),
                "response_hex": response_bytes.hex(" "),
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "is_success": True,
                "error_message": "",
            }
        except Exception as exc:
            return {
                "protocol": ApiProtocol.TCP,
                "method": "",
                "headers": {},
                "response_status": "",
                "response_headers": {},
                "response_text": "",
                "response_hex": response_bytes.hex(" "),
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "is_success": False,
                "error_message": str(exc),
            }

    def _execute_websocket(self, cleaned_data):
        started = time.perf_counter()
        headers = platform_auth_headers(self.user)
        headers.update(self._parse_headers(cleaned_data["headers"]))

        async def runner():
            if websockets is None:
                raise RuntimeError("websockets package is not installed")
            async with websockets.connect(cleaned_data["target"], additional_headers=headers, open_timeout=10) as websocket:
                if cleaned_data["request_payload"]:
                    await websocket.send(cleaned_data["request_payload"])
                return await asyncio.wait_for(websocket.recv(), timeout=10)

        try:
            response = asyncio.run(runner())
            response_text = response if isinstance(response, str) else response.decode("utf-8", errors="replace")
            response_hex = response.encode("utf-8").hex(" ") if isinstance(response, str) else response.hex(" ")
            return {
                "protocol": ApiProtocol.WEBSOCKET,
                "method": "",
                "headers": headers,
                "response_status": "WS_OK",
                "response_headers": {},
                "response_text": response_text,
                "response_hex": response_hex,
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "is_success": True,
                "error_message": "",
            }
        except Exception as exc:
            return {
                "protocol": ApiProtocol.WEBSOCKET,
                "method": "",
                "headers": headers,
                "response_status": "",
                "response_headers": {},
                "response_text": "",
                "response_hex": "",
                "duration_ms": int((time.perf_counter() - started) * 1000),
                "is_success": False,
                "error_message": str(exc),
            }
